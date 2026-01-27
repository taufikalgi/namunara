from datetime import datetime
from sqlalchemy import ForeignKey, BigInteger, Integer, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class MessageMappingModel(Base):
    __tablename__ = "message_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_message_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True
    )
    original_channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    translated_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    translation_channel_id: Mapped[int] = mapped_column(
        ForeignKey("translation_channels.id")
    )
    translation_channel: Mapped["TranslationChannelModel"] = relationship(
        "TranslationChannelModel"
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
