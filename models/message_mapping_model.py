from sqlalchemy import ForeignKey, String, BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class MessageMappingModel(Base):
    __tablename__ = "message_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
