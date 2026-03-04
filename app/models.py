from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Destination(Base):
    __tablename__ = "destinations"

    __table_args__ = (
        UniqueConstraint("name", "country", "type", name="uq_destination_name_country_type"),
        CheckConstraint("avg_cost_usd IS NULL OR avg_cost_usd >= 0", name="ck_dest_cost_nonneg"),
        CheckConstraint("rating IS NULL OR (rating >= 0 AND rating <= 5)", name="ck_dest_rating_range"),
        CheckConstraint(
            "annual_visitors_m IS NULL OR annual_visitors_m >= 0",
            name="ck_dest_visitors_nonneg",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    continent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    best_season: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    avg_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    annual_visitors_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    unesco: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Backref from WishlistItem
    wishlist_items: Mapped[List["WishlistItem"]] = relationship(
        back_populates="destination",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(320), nullable=False)  # max email length ~320
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    wishlists: Mapped[List["Wishlist"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Wishlist(Base):
    __tablename__ = "wishlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="wishlists")

    items: Mapped[List["WishlistItem"]] = relationship(
        back_populates="wishlist",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    __table_args__ = (
        UniqueConstraint("wishlist_id", "destination_id", name="uq_wishlist_destination"),
        CheckConstraint("priority IS NULL OR priority >= 0", name="ck_item_priority_nonneg"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    wishlist_id: Mapped[int] = mapped_column(
        ForeignKey("wishlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey("destinations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    wishlist: Mapped["Wishlist"] = relationship(back_populates="items")
    destination: Mapped["Destination"] = relationship(back_populates="wishlist_items")