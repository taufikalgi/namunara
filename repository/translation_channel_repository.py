from models import GuildModel, TranslationChannelModel
from repository.guild_repository import get_guild_by_guild_id
from sqlalchemy.ext.asyncio import AsyncSession

async def add_translation_channel(session: AsyncSession, new_translation_channel: TranslationChannelModel):
    session.add(new_translation_channel)
    await session.commit()
    