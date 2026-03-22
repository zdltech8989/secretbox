from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix='/api/secrets', tags=['secrets'])


class SecretCreate(BaseModel):
    name: str
    value: str
    category_id: Optional[int] = None
    notes: Optional[str] = None
    url: Optional[str] = None
    remark: Optional[str] = None

class SecretUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None
    url: Optional[str] = None
    remark: Optional[str] = None


@router.get('')
async def list_secrets(
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
):
    from services.secret_service import SecretService
    svc = SecretService(user_id=user.id)
    return await svc.list_all(category_id=category_id, keyword=keyword)


@router.get('/item/{secret_id}')
async def get_secret(secret_id: int, user: User = Depends(get_current_user)):
    from services.secret_service import SecretService
    svc = SecretService(user_id=user.id)
    try:
        result = await svc.get(secret_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not result:
        raise HTTPException(404, 'Secret not found')
    return result


@router.post('')
async def create_secret(req: SecretCreate, user: User = Depends(get_current_user)):
    from services.secret_service import SecretService
    svc = SecretService(user_id=user.id)
    try:
        return await svc.create(
            name=req.name, value=req.value, category_id=req.category_id,
            notes=req.notes, url=req.url, remark=req.remark,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put('/{secret_id}')
async def update_secret(secret_id: int, req: SecretUpdate, user: User = Depends(get_current_user)):
    from services.secret_service import SecretService
    svc = SecretService(user_id=user.id)
    fields = {k: v for k, v in req.model_dump().items() if v is not None}
    try:
        result = await svc.update(secret_id, **fields)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not result:
        raise HTTPException(404, 'Secret not found')
    return result


@router.delete('/{secret_id}')
async def delete_secret(secret_id: int, user: User = Depends(get_current_user)):
    from services.secret_service import SecretService
    svc = SecretService(user_id=user.id)
    ok = await svc.delete(secret_id)
    if not ok:
        raise HTTPException(404, 'Secret not found')
    return {'message': 'Secret deleted'}


@router.get('/q/{keyword}')
async def search_secrets(keyword: str, user: User = Depends(get_current_user)):
    from services.secret_service import SecretService
    svc = SecretService(user_id=user.id)
    return await svc.search(keyword)
