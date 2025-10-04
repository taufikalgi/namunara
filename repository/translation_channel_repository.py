from models import GuildModel, TranslationChannelModel
from repository.guild_repository import get_guild_by_guild_id
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def add_translation_channel(session: AsyncSession, new_translation_channel: TranslationChannelModel):
    session.add(new_translation_channel)
    await session.commit()
    
async def get_translation_channel_by_guild_id(session: AsyncSession, guild_id: int):
    try:
        result = await session.execute(
            select(TranslationChannelModel).where(TranslationChannelModel.guild_id == guild_id)
        )
        return result.scalars().all()
    
    except Exception as e:
        print(f"Error fetching translations channels for guild {guild_id}: {e}")
        return []
