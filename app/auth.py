from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.crypto import derive_key, hash_password
from app.models import MasterKey, User
from app.database import AsyncSessionLocal
from sqlalchemy import select

_cached_key: bytes | None = None
_cached_salt: bytes | None = None
_bearer = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


async def is_master_password_set() -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MasterKey).limit(1))
        return result.scalar_one_or_none() is not None


async def setup_master_password(password: str) -> dict:
    global _cached_key, _cached_salt
    from app.crypto import _ITERATIONS
    key, salt = derive_key(password, iterations=_ITERATIONS)
    _cached_key = key
    _cached_salt = salt
    salt_b64 = salt.hex()
    vhash = hash_password(password)
    async with AsyncSessionLocal() as session:
        mk = MasterKey(salt=salt_b64, verify_hash=vhash, iterations=_ITERATIONS)
        session.add(mk)
        await session.commit()
    token = create_access_token({'sub': 'master', 'user_id': 0, 'username': 'master', 'is_admin': True})
    return {'token': token, 'message': 'Master password set successfully'}


async def verify_master_password(password: str) -> dict:
    global _cached_key, _cached_salt
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MasterKey).limit(1))
        mk = result.scalar_one_or_none()
        if not mk:
            return {'error': 'Master password not set'}
        stored_iterations = mk.iterations
        vhash = hash_password(password)
        if vhash != mk.verify_hash:
            return {'error': 'Invalid master password'}
        salt = bytes.fromhex(mk.salt)
        key, _ = derive_key(password, salt, iterations=stored_iterations)
        _cached_key = key
        _cached_salt = salt
    token = create_access_token({'sub': 'master', 'user_id': 0, 'username': 'master', 'is_admin': True})
    return {'token': token}


async def change_master_password(old_password: str, new_password: str) -> dict:
    global _cached_key, _cached_salt
    from app.crypto import _ITERATIONS
    key, salt = derive_key(new_password, iterations=_ITERATIONS)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MasterKey).limit(1))
        mk = result.scalar_one_or_none()
        if not mk:
            return {'error': 'Master password not set'}
        if hash_password(old_password) != mk.verify_hash:
            return {'error': 'Invalid old password'}
        mk.salt = salt.hex()
        mk.verify_hash = hash_password(new_password)
        mk.iterations = _ITERATIONS
        await session.commit()
    _cached_key = key
    _cached_salt = salt
    return {'message': 'Master password changed successfully'}


def get_current_token(authorization: str = Header(default='')) -> str:
    token = authorization.replace('Bearer ', '') if authorization.startswith('Bearer ') else authorization
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing authentication token')
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')
    return token


async def verify_user_login(username: str, password: str) -> dict:
    """验证用户名密码登录，返回 token 或 error。"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
    if not user:
        return {'error': '用户名或密码错误'}
    if hash_password(password) != user.password_hash:
        return {'error': '用户名或密码错误'}
    token = create_access_token({
        'sub': 'user',
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin,
    })
    return {'token': token}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User | None:
    """从 JWT 解析当前用户，返回 User 对象。支持 master 和 user 两种 token。"""
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    sub = payload.get('sub')
    if sub == 'master':
        return User(id=0, username='master', password_hash='', is_admin=True)
    if sub == 'user':
        user_id = payload.get('user_id')
        if not user_id:
            return None
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
        return user
    return None


def require_admin(user: User | None = Depends(get_current_user)) -> User:
    """依赖注入：要求当前用户是管理员。"""
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='未登录')
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无管理员权限')
    return user
