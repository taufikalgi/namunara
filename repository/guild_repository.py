from models import GuildModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def add_guild(session: AsyncSession, new_guild: GuildModel):
    session.add(new_guild)
    await session.commit()


async def get_guild_by_id(session: AsyncSession, id: int):
    try:
        result = await session.execute(select(GuildModel).where(GuildModel.id == id))
        guild = result.scalar_one_or_none()

    except Exception as e:
        print(print(f"Cannot get guild by id: {id} {e}"))

    return guild


async def get_guild_allow_translation_by_id(session: AsyncSession, id: int):
    try:
        result = await session.execute(
            select(GuildModel.allow_translation).where(GuildModel.id == id)
        )
        allow_translation = result.scalar_one_or_none()

    except Exception as e:
        print(f"Cannot get guild allow_translation by id: {id} {e}")

    return allow_translation


async def delete_guild(session: AsyncSession, guild: GuildModel):
    try:
        await session.delete(guild)

    except Exception as e:
        print(f"Cannot delete {guild.name} ({guild.guild_id}) {e}")
