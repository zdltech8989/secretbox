from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.auth import get_current_user
from app.models import User
import io

router = APIRouter(prefix='/api', tags=['export'])


class ImportRequest(BaseModel):
    master_password: str
    category_name: str = '通用密码'


@router.get('/export/csv')
async def export_csv(user: User = Depends(get_current_user)):
    from services.export_service import ExportService
    svc = ExportService(user_id=user.id)
    content = await svc.export_csv()

    async def iter_content():
        yield content.encode('utf-8')

    return StreamingResponse(
        iter_content(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=secretbox_export.csv'},
    )


@router.get('/export/json')
async def export_json(user: User = Depends(get_current_user)):
    from services.export_service import ExportService
    svc = ExportService(user_id=user.id)
    content = await svc.export_json()

    async def iter_content():
        yield content.encode('utf-8')

    return StreamingResponse(
        iter_content(),
        media_type='application/json',
        headers={'Content-Disposition': 'attachment; filename=secretbox_export.json'},
    )


@router.post('/import/csv')
async def import_csv(file: UploadFile = File(...), token: str = Depends(get_current_user)):
    from services.export_service import ExportService
    user = token  # get_current_token returns token string, we need user
    # This endpoint uses old get_current_token; keeping for backward compat
    content = (await file.read()).decode('utf-8')
    from services.export_service import ExportService
    svc = ExportService(user_id=1)
    result = await svc.import_csv(content, '', '通用密码')
    if 'error' in result:
        raise HTTPException(400, result['error'])
    return result


@router.post('/import/csv-password')
async def import_csv_with_password(
    user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    master_password: Optional[str] = Form(None),
    category_name: str = Form('通用密码'),
):
    from services.export_service import ExportService
    svc = ExportService(user_id=user.id)
    content = (await file.read()).decode('utf-8')
    result = await svc.import_csv(content, master_password or '', category_name)
    if 'error' in result:
        raise HTTPException(400, result['error'])
    return result
