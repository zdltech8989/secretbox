import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, text

from app.config import DATABASE_URL, DATA_DIR
from app.models import Base, MasterKey, Category, User
from app.crypto import hash_password, derive_key, _ITERATIONS

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

DEFAULT_CATEGORIES = [
    ('OpenAI', 'bot', 1),
    ('Claude', 'brain', 2),
    ('Gemini', 'sparkles', 3),
    ('DeepSeek', 'flame', 4),
    ('通用密码', 'lock', 10),
    ('API Token', 'key', 11),
    ('SSH Key', 'terminal', 12),
    ('数据库', 'database', 13),
]


async def _ensure_default_categories(session, user_id: int):
    """为指定用户初始化默认分类。"""
    result = await session.execute(
        select(Category).where(Category.user_id == user_id)
    )
    existing = {c.name for c in result.scalars().all()}
    for name, icon, order in DEFAULT_CATEGORIES:
        if name not in existing:
            session.add(Category(name=name, icon=icon, sort_order=order, user_id=user_id))


async def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 迁移：为旧 MasterKey 表添加 iterations 列，默认值 600000 兼容旧数据
        try:
            await conn.execute(text('ALTER TABLE master_keys ADD COLUMN iterations INTEGER DEFAULT 600000 NOT NULL'))
        except Exception:
            pass  # 列已存在则忽略

    async with AsyncSessionLocal() as session:
        # 初始化主密码 (密码: a123456)
        result = await session.execute(select(MasterKey).limit(1))
        mk = result.scalar_one_or_none()
        if not mk:
            key, salt = derive_key('a123456')
            mk = MasterKey(salt=salt.hex(), verify_hash=hash_password('a123456'), iterations=_ITERATIONS)
            session.add(mk)
        else:
            # 检查是否有旧的 MasterKey 没有设置 iterations 列的默认值
            # 虽然 ALTER TABLE 设置了 DEFAULT 600000，但已有记录的 iterations 可能是 NULL
            if mk.iterations is None:
                mk.iterations = 600000  # 旧数据使用 600000 迭代

        # 初始化管理员账号
        result = await session.execute(select(User).where(User.username == 'zhangdl'))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username='zhangdl',
                password_hash=hash_password('a123456'),
                is_admin=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

        # 为管理员初始化默认分类
        await _ensure_default_categories(session, admin.id)
        await session.commit()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
