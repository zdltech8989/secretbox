from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix='/api/categories', tags=['categories'])


class CategoryCreate(BaseModel):
    name: str
    icon: str = 'tag'

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None


@router.get('')
async def list_categories(user: User = Depends(get_current_user)):
    from services.category_service import CategoryService
    svc = CategoryService(user_id=user.id)
    return await svc.list_all()


@router.get('/{category_id}')
async def get_category(category_id: int, user: User = Depends(get_current_user)):
    from services.category_service import CategoryService
    svc = CategoryService(user_id=user.id)
    result = await svc.get(category_id)
    if not result:
        raise HTTPException(404, 'Category not found')
    return result


@router.post('')
async def create_category(req: CategoryCreate, user: User = Depends(get_current_user)):
    from services.category_service import CategoryService
    svc = CategoryService(user_id=user.id)
    return await svc.create(req.name, req.icon)


@router.put('/{category_id}')
async def update_category(category_id: int, req: CategoryUpdate, user: User = Depends(get_current_user)):
    from services.category_service import CategoryService
    svc = CategoryService(user_id=user.id)
    result = await svc.update(category_id, req.name, req.icon)
    if not result:
        raise HTTPException(404, 'Category not found')
    return result


@router.delete('/{category_id}')
async def delete_category(category_id: int, user: User = Depends(get_current_user)):
    from services.category_service import CategoryService
    svc = CategoryService(user_id=user.id)
    ok = await svc.delete(category_id)
    if not ok:
        raise HTTPException(404, 'Category not found')
    return {'message': 'Category deleted'}
