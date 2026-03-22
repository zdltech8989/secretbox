from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer, String, DateTime, Text, ForeignKey, func, Boolean
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MasterKey(Base):
    __tablename__ = 'master_keys'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    salt: Mapped[str] = mapped_column(Text, nullable=False)
    verify_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    iterations: Mapped[int] = mapped_column(Integer, default=100000, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default='folder')
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    secrets: Mapped[list['Secret']] = relationship('Secret', back_populates='category')


class Secret(Base):
    __tablename__ = 'secrets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('categories.id'), nullable=True
    )
    encrypted_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_nonce: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    remark: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[Optional['Category']] = relationship('Category', back_populates='secrets')
