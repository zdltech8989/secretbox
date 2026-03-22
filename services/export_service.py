import csv
import io
import json
from typing import Optional
from app.models import Secret, Category
from app.database import AsyncSessionLocal
from app.crypto import encrypt
from app import auth as auth_module
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class ExportService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def export_csv(self) -> str:
        secrets = await self._get_all_decrypted()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['name', 'url', 'value', 'remark', 'category', 'notes', 'created_at'])
        for s in secrets:
            writer.writerow([
                s['name'], s.get('url', ''), s['value'], s.get('remark', ''),
                s.get('category_name', ''), s.get('notes', ''), s.get('created_at', ''),
            ])
        return output.getvalue()

    async def export_json(self) -> str:
        secrets = await self._get_all_decrypted()
        return json.dumps(secrets, ensure_ascii=False, indent=2)

    async def import_csv(self, csv_content: str, master_password: str = '', category_name: str = '通用密码') -> dict:
        from app.crypto import encrypt, derive_key, hash_password
        from app.models import MasterKey
        from sqlalchemy import select

        # 获取加密密钥：优先使用缓存的，如果没有则用密码派生
        key = auth_module._cached_key
        if not key and master_password:
            # 派生密钥
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(MasterKey).limit(1))
                mk = result.scalar_one_or_none()
                if not mk:
                    return {'error': '主密码未设置'}
                if hash_password(master_password) != mk.verify_hash:
                    return {'error': '主密码错误'}
                salt = bytes.fromhex(mk.salt)
                key, _ = derive_key(master_password, salt, iterations=mk.iterations)

        if not key:
            return {'error': '请先解锁保险箱'}

        reader = csv.DictReader(io.StringIO(csv_content))
        imported = 0
        async with AsyncSessionLocal() as session:
            cat_result = await session.execute(
                select(Category).where(
                    Category.name == category_name,
                    Category.user_id == self.user_id,
                )
            )
            category = cat_result.scalar_one_or_none()

            for row in reader:
                name = (row.get('name') or '').strip()
                value = row.get('password') or row.get('value', '')
                url = (row.get('url') or '').strip()
                remark = row.get('username') or row.get('remark', '')
                if not name and url:
                    name = url
                if not name:
                    continue
                ct, nonce = encrypt(value, key)
                secret = Secret(
                    name=name,
                    encrypted_value=ct,
                    nonce=nonce,
                    category_id=category.id if category else None,
                    url=url or None,
                    remark=remark or None,
                    user_id=self.user_id,
                )
                session.add(secret)
                imported += 1
            await session.commit()
        return {'imported': imported, 'message': f'成功导入 {imported} 条密钥'}

    async def _get_all_decrypted(self) -> list[dict]:
        from app.crypto import decrypt

        if not auth_module._cached_key:
            return []
        key = auth_module._cached_key
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Secret)
                .options(selectinload(Secret.category))
                .where(Secret.user_id == self.user_id)
                .order_by(Secret.updated_at.desc())
            )
            secrets = result.scalars().all()
            out = []
            for s in secrets:
                value = decrypt(s.encrypted_value, s.nonce, key)
                notes = ''
                if s.encrypted_notes and s.notes_nonce:
                    notes = decrypt(s.encrypted_notes, s.notes_nonce, key)
                cat_name = s.category.name if s.category else ''
                out.append({
                    'id': s.id,
                    'name': s.name,
                    'value': value,
                    'url': s.url,
                    'remark': s.remark,
                    'category_name': cat_name,
                    'notes': notes,
                    'created_at': str(s.created_at),
                })
            return out
