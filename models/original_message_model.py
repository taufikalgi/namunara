from datetime import datetime
from sqlalchemy import BigInteger, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class OriginalMessageModel(Base):
    __tablename__ = "original_messages"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=False
    )
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
