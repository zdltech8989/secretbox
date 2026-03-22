from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.auth import (
    is_master_password_set, setup_master_password,
    verify_master_password, change_master_password, get_current_token,
    create_access_token, verify_user_login, get_current_user,
)
from app import auth as auth_module
from app.crypto import hash_password, derive_key, encrypt, decrypt, _ITERATIONS
from app.database import AsyncSessionLocal
from app.models import User, MasterKey, Secret
from sqlalchemy import select

router = APIRouter(prefix='/api/auth', tags=['auth'])


class SetupRequest(BaseModel):
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UnlockVaultRequest(BaseModel):
    master_password: str

class ResetMasterPasswordRequest(BaseModel):
    old_master_password: str
    new_master_password: str


@router.get('/status')
async def auth_status(user: User = Depends(get_current_user)):
    """检查主密码是否已设置（需登录）。"""
    if not user:
        raise HTTPException(401, '未登录')
    set = await is_master_password_set()
    return {'initialized': set}


@router.post('/setup')
async def setup(req: SetupRequest, user: User = Depends(get_current_user)):
    """登录后设置主密码（仅首次）。"""
    if not user:
        raise HTTPException(401, '未登录')
    already = await is_master_password_set()
    if already:
        raise HTTPException(400, '主密码已设置')
    return await setup_master_password(req.password)


@router.post('/login')
async def login(req: LoginRequest):
    # 每次登录清除加密密钥缓存，强制重新解锁
    auth_module._cached_key = None
    result = await verify_user_login(req.username, req.password)
    if 'error' in result:
        raise HTTPException(401, result['error'])
    return result


@router.post('/unlock-vault')
async def unlock_vault(req: UnlockVaultRequest, user: User = Depends(get_current_user)):
    """输入主密码解锁加密密钥。"""
    if not user:
        raise HTTPException(401, '未登录')
    import logging
    logger = logging.getLogger(__name__)
    # 在 session 内完成所有数据库操作，避免 session 关闭后访问分离对象报错
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MasterKey).limit(1))
        mk = result.scalar_one_or_none()
        if not mk:
            raise HTTPException(400, '主密码未设置')
        if hash_password(req.master_password) != mk.verify_hash:
            logger.warning(f"主密码验证失败：用户={user.username}")
            raise HTTPException(401, '主密码错误')
        verify_hash = mk.verify_hash
        salt_hex = mk.salt
        stored_iterations = mk.iterations
        logger.info(f"开始派生密钥：迭代次数={stored_iterations}")
    salt = bytes.fromhex(salt_hex)
    key, _ = derive_key(req.master_password, salt, iterations=stored_iterations)
    auth_module._cached_key = key
    logger.info(f"密钥派生完成，用户={user.username}")
    return {'message': '保险箱已解锁'}


@router.get('/vault-status')
async def vault_status(user: User = Depends(get_current_user)):
    """检查加密密钥是否已解锁。"""
    if not user:
        raise HTTPException(401, '未登录')
    return {'unlocked': auth_module._cached_key is not None}


@router.post('/change-password')
async def change_pwd(req: ChangePasswordRequest, user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(401, '未登录')
    if user.username == 'master':
        result = await change_master_password(req.old_password, req.new_password)
        if 'error' in result:
            raise HTTPException(400, result['error'])
        new_token = create_access_token({'sub': 'master', 'user_id': 0, 'username': 'master', 'is_admin': True})
        return {**result, 'token': new_token}
    else:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user.id))
            db_user = result.scalar_one_or_none()
            if not db_user:
                raise HTTPException(400, '用户不存在')
            if hash_password(req.old_password) != db_user.password_hash:
                raise HTTPException(400, '旧密码错误')
            db_user.password_hash = hash_password(req.new_password)
            await session.commit()
        new_token = create_access_token({
            'sub': 'user', 'user_id': db_user.id,
            'username': db_user.username, 'is_admin': db_user.is_admin,
        })
        return {'message': '密码修改成功', 'token': new_token}


@router.get('/me')
async def get_me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(401, '未登录')
    return {
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin,
    }


@router.post('/reset-master-password')
async def reset_master_password(req: ResetMasterPasswordRequest, user: User = Depends(get_current_user)):
    """重置主密码，同时重新加密所有已存储的密钥。需要 vault 已解锁。"""
    if not user:
        raise HTTPException(401, '未登录')
    if not auth_module._cached_key:
        raise HTTPException(400, '请先解锁保险箱')

    old_key = auth_module._cached_key
    new_key, new_salt = derive_key(req.new_master_password, iterations=_ITERATIONS)

    # 在同一个 session 中：验证旧密码、重新加密 secret、更新 MasterKey
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MasterKey).limit(1))
        mk = result.scalar_one_or_none()
        if not mk:
            raise HTTPException(400, '主密码未设置')
        if hash_password(req.old_master_password) != mk.verify_hash:
            raise HTTPException(400, '旧主密码错误')

        # 重新加密所有 secret
        result = await session.execute(select(Secret))
        secrets = result.scalars().all()
        count = 0
        for s in secrets:
            value = decrypt(s.encrypted_value, s.nonce, old_key)
            ct, nonce = encrypt(value, new_key)
            s.encrypted_value = ct
            s.nonce = nonce
            if s.encrypted_notes and s.notes_nonce:
                notes = decrypt(s.encrypted_notes, s.notes_nonce, old_key)
                enc_notes, notes_nonce = encrypt(notes, new_key)
                s.encrypted_notes = enc_notes
                s.notes_nonce = notes_nonce
            count += 1

        # 更新 MasterKey
        mk.salt = new_salt.hex()
        mk.verify_hash = hash_password(req.new_master_password)
        mk.iterations = _ITERATIONS

        await session.commit()

    auth_module._cached_key = new_key
    return {'message': f'主密码已重置，已重新加密 {count} 条密钥'}
