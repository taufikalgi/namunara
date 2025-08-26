from models import GuildModel, TranslationChannelModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def add_guild(session: AsyncSession, new_guild: GuildModel):
    session.add(new_guild)
    await session.commit()

async def get_guild_by_guild_id(session: AsyncSession, guild_id):
    try:
        result = await session.execute(
            select(GuildModel).where(GuildModel.guild_id == guild_id)
        )
        guild = result.scalar_one_or_none()
        
    except Exception as e:
        print(print(f"Cannot get guild by guild_id: {guild_id} {e}"))
    
    return guild

async def get_guild_allow_translation_by_guild_id(session: AsyncSession, guild_id):
    try:
        result = await session.execute(
            select(GuildModel.allow_translation).where(GuildModel.guild_id == guild_id)
        )
        allow_translation = result.scalar_one_or_none()

    except Exception as e:
        print(f"Cannot get guild allow_translation by guild_id: {guild_id} {e}")

    return allow_translation

async def delete_guild(session: AsyncSession, guild: GuildModel):
    try:
        await session.delete(guild)
        await session.commit()

    except Exception as e:
        print(f"Cannot delete {guild.name} ({guild.guild_id}) {e}")
    
async def add_translation_channel(session: AsyncSession, guild_id: int, guild_name: str, channel_id: int, lang: str):
    guild = await session.get(GuildModel, guild_id)
    if not guild:
        guild = GuildModel(guild_id=guild_id, name=guild_name)
        session.add(guild)

    channel = TranslationChannelModel(channel_id=channel_id, language=lang, guild=guild)
    session.add(channel)

    await session.commit()