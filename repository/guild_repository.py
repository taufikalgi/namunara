from models import GuildModel, TranslationChannelModel
from sqlalchemy.ext.asyncio import AsyncSession

async def add_guild(session: AsyncSession, new_guild: GuildModel):
    session.add(new_guild)
    await session.commit()
    
async def add_translation_channel(session: AsyncSession, guild_id: int, guild_name: str, channel_id: int, lang: str):
    guild = await session.get(GuildModel, guild_id)
    if not guild:
        guild = GuildModel(guild_id=guild_id, name=guild_name)
        session.add(guild)

    channel = TranslationChannelModel(channel_id=channel_id, language=lang, guild=guild)
    session.add(channel)

    await session.commit()