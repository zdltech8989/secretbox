from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.auth import get_current_user, require_admin, create_access_token
from app.crypto import hash_password
from app.database import AsyncSessionLocal, _ensure_default_categories
from app.models import User, Category
from sqlalchemy import select

router = APIRouter(prefix='/api/users', tags=['users'])


class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class ResetPasswordRequest(BaseModel):
    new_password: str


class ChangeOwnPasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.get('')
async def list_users(admin: User = Depends(require_admin)):
    """获取所有用户列表（仅管理员）。"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).order_by(User.created_at))
        users = result.scalars().all()
    return [{
        'id': u.id,
        'username': u.username,
        'is_admin': u.is_admin,
        'created_at': u.created_at.isoformat() if u.created_at else None,
    } for u in users]


@router.post('')
async def create_user(req: CreateUserRequest, admin: User = Depends(require_admin)):
    """创建新用户（仅管理员）。"""
    if len(req.username.strip()) < 2:
        raise HTTPException(400, '用户名至少 2 个字符')
    if len(req.password) < 6:
        raise HTTPException(400, '密码至少 6 个字符')
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(User).where(User.username == req.username.strip()))
        if existing.scalar_one_or_none():
            raise HTTPException(400, '用户名已存在')
        user = User(
            username=req.username.strip(),
            password_hash=hash_password(req.password),
            is_admin=req.is_admin,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        # 为新用户初始化默认分类
        await _ensure_default_categories(session, user.id)
        await session.commit()
    return {
        'id': user.id,
        'username': user.username,
        'is_admin': user.is_admin,
        'message': '用户创建成功',
    }


@router.put('/{user_id}/reset-password')
async def reset_password(user_id: int, req: ResetPasswordRequest, admin: User = Depends(require_admin)):
    """重置用户密码（仅管理员）。"""
    if len(req.new_password) < 6:
        raise HTTPException(400, '密码至少 6 个字符')
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, '用户不存在')
        user.password_hash = hash_password(req.new_password)
        await session.commit()
    return {'message': f'用户 {user.username} 的密码已重置'}


@router.delete('/{user_id}')
async def delete_user(user_id: int, admin: User = Depends(require_admin)):
    """删除用户（仅管理员，不能删除自己）。"""
    if admin.id == user_id:
        raise HTTPException(400, '不能删除自己')
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, '用户不存在')
        username = user.username
        await session.delete(user)
        await session.commit()
    return {'message': f'用户 {username} 已删除'}
