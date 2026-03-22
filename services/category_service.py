from typing import Optional
from sqlalchemy import select, func
from app.models import Category, Secret
from app.database import AsyncSessionLocal


class CategoryService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def list_all(self) -> list[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Category)
                .where(Category.user_id == self.user_id)
                .order_by(Category.sort_order)
            )
            categories = result.scalars().all()
            out = []
            for c in categories:
                cnt = await session.execute(
                    select(func.count()).where(
                        Secret.category_id == c.id,
                        Secret.user_id == self.user_id,
                    )
                )
                out.append({
                    'id': c.id,
                    'name': c.name,
                    'icon': c.icon,
                    'sort_order': c.sort_order,
                    'secret_count': cnt.scalar(),
                })
            return out

    async def get(self, category_id: int) -> dict | None:
        async with AsyncSessionLocal() as session:
            c = await session.get(Category, category_id)
            if not c or c.user_id != self.user_id:
                return None
            cnt = await session.execute(
                select(func.count()).where(
                    Secret.category_id == c.id,
                    Secret.user_id == self.user_id,
                )
            )
            return {
                'id': c.id,
                'name': c.name,
                'icon': c.icon,
                'sort_order': c.sort_order,
                'secret_count': cnt.scalar(),
            }

    async def create(self, name: str, icon: str = 'tag') -> dict:
        async with AsyncSessionLocal() as session:
            cat = Category(name=name, icon=icon, user_id=self.user_id)
            session.add(cat)
            await session.commit()
            await session.refresh(cat)
            return {'id': cat.id, 'name': cat.name, 'icon': cat.icon, 'message': 'Category created'}

    async def update(self, category_id: int, name: Optional[str] = None, icon: Optional[str] = None) -> dict | None:
        async with AsyncSessionLocal() as session:
            cat = await session.get(Category, category_id)
            if not cat or cat.user_id != self.user_id:
                return None
            if name is not None:
                cat.name = name
            if icon is not None:
                cat.icon = icon
            await session.commit()
            return {'id': cat.id, 'message': 'Category updated'}

    async def delete(self, category_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            cat = await session.get(Category, category_id)
            if not cat or cat.user_id != self.user_id:
                return False
            await session.delete(cat)
            await session.commit()
            return True
