from sqlalchemy import ForeignKey, String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
