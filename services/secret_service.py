from typing import Optional
from sqlalchemy import select, func, or_
from app.models import Secret, MasterKey
from app.crypto import encrypt, decrypt, derive_key
from app.database import AsyncSessionLocal


async def _get_encryption_key() -> bytes:
    from app.auth import _cached_key
    if _cached_key:
        return _cached_key
    raise ValueError('Encryption key not available. Please unlock vault first.')


class SecretService:
    def __init__(self, user_id: int, master_password: str | None = None):
        self.user_id = user_id
        self._key_promise = master_password

    async def _key(self) -> bytes:
        from app.auth import _cached_key
        if _cached_key:
            return _cached_key
        if self._key_promise:
            return await _get_encryption_key_from_password(self._key_promise)
        return await _get_encryption_key()

    async def create(
        self,
        name: str,
        value: str,
        category_id: Optional[int] = None,
        notes: Optional[str] = None,
        url: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> dict:
        key = await self._key()
        ct, nonce = encrypt(value, key)
        enc_notes, notes_nonce = encrypt(notes, key) if notes else (None, None)

        async with AsyncSessionLocal() as session:
            secret = Secret(
                name=name,
                encrypted_value=ct,
                nonce=nonce,
                category_id=category_id,
                encrypted_notes=enc_notes,
                notes_nonce=notes_nonce,
                url=url,
                remark=remark,
                user_id=self.user_id,
            )
            session.add(secret)
            await session.commit()
            await session.refresh(secret)
            return {'id': secret.id, 'name': name, 'message': 'Secret created'}

    async def get(self, secret_id: int) -> dict | None:
        key = await self._key()
        async with AsyncSessionLocal() as session:
            secret = await session.get(Secret, secret_id)
            if not secret or secret.user_id != self.user_id:
                return None
            value = decrypt(secret.encrypted_value, secret.nonce, key)
            notes = None
            if secret.encrypted_notes and secret.notes_nonce:
                notes = decrypt(secret.encrypted_notes, secret.notes_nonce, key)
            return {
                'id': secret.id,
                'name': secret.name,
                'value': value,
                'category_id': secret.category_id,
                'notes': notes,
                'url': secret.url,
                'remark': secret.remark,
                'created_at': str(secret.created_at),
                'updated_at': str(secret.updated_at),
            }

    async def list_all(
        self, category_id: Optional[int] = None, keyword: Optional[str] = None
    ) -> list[dict]:
        async with AsyncSessionLocal() as session:
            q = select(Secret).where(Secret.user_id == self.user_id)
            if category_id:
                q = q.where(Secret.category_id == category_id)
            if keyword:
                # 多字段搜索：name, url, remark
                search_condition = or_(
                    Secret.name.ilike(f'%{keyword}%'),
                    Secret.url.ilike(f'%{keyword}%'),
                    Secret.remark.ilike(f'%{keyword}%')
                )
                q = q.where(search_condition)
            q = q.order_by(Secret.updated_at.desc())
            print(f"[DEBUG] category_id={category_id}, keyword={keyword}")
            result = await session.execute(q)
            secrets = result.scalars().all()
            print(f"[DEBUG] Found {len(secrets)} secrets")
            return [
                {
                    'id': s.id,
                    'name': s.name,
                    'category_id': s.category_id,
                    'url': s.url,
                    'remark': s.remark,
                    'created_at': str(s.created_at),
                    'updated_at': str(s.updated_at),
                }
                for s in secrets
            ]

    async def update(self, secret_id: int, **fields) -> dict | None:
        key = await self._key()
        async with AsyncSessionLocal() as session:
            secret = await session.get(Secret, secret_id)
            if not secret or secret.user_id != self.user_id:
                return None
            if 'name' in fields:
                secret.name = fields['name']
            if 'value' in fields:
                ct, nonce = encrypt(fields['value'], key)
                secret.encrypted_value = ct
                secret.nonce = nonce
            if 'category_id' in fields:
                secret.category_id = fields['category_id']
            if 'notes' in fields:
                if fields['notes']:
                    ct, nonce = encrypt(fields['notes'], key)
                    secret.encrypted_notes = ct
                    secret.notes_nonce = nonce
                else:
                    secret.encrypted_notes = None
                    secret.notes_nonce = None
            if 'url' in fields:
                secret.url = fields['url']
            if 'remark' in fields:
                secret.remark = fields['remark']
            await session.commit()
            return {'id': secret.id, 'message': 'Secret updated'}

    async def delete(self, secret_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            secret = await session.get(Secret, secret_id)
            if not secret or secret.user_id != self.user_id:
                return False
            await session.delete(secret)
            await session.commit()
            return True

    async def search(self, keyword: str) -> list[dict]:
        """搜索包含关键词的密钥记录（在 name、url、remark 字段中搜索）"""
        return await self.list_all(keyword=keyword)
