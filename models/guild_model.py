from typing import List
from sqlalchemy import String, BigInteger, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base



class GuildModel(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String)
    allow_translation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    translation_channels: Mapped[List["TranslationChannelModel"]] = relationship(
        "TranslationChannelModel",
        back_populates="guild",
        cascade="all, delete-orphan"
    )
    