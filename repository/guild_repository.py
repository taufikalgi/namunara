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


async def get_id_by_guild_id(session: AsyncSession, guild_id: int):
    try:
        result = await session.execute(
            select(GuildModel.id).where(GuildModel.guild_id == guild_id)
        )
        return result.scalars().first()

    except Exception as e:
        print(f"Error fetching guild id for guild_id {guild_id}: {e}")
        return None
