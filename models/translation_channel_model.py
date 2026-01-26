from datetime import datetime
from sqlalchemy import ForeignKey, String, BigInteger, Integer, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .base import Base


class TranslationChannelModel(Base):
    __tablename__ = "translation_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    language: Mapped[str] = mapped_column(String)

    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"))
    guild: Mapped["GuildModel"] = relationship(
        "GuildModel", back_populates="translation_channels"
    )
    message_mappings: Mapped[List["MessageMappingModel"]] = relationship(
        "MessageMappingModel",
        back_populates="translation_channel",
        cascade="all, delete-orphan",
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
