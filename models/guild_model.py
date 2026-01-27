from datetime import datetime
from sqlalchemy import String, BigInteger, Boolean, Integer, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .base import Base


class GuildModel(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String)
    allow_translation: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    translation_channels: Mapped[List["TranslationChannelModel"]] = relationship(
        "TranslationChannelModel", back_populates="guild", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
