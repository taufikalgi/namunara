from discord.ext import commands
from models import GuildModel
from repository.guild_repository import *
from repository.db import async_session
import discord

class GuildCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()

        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Guild cog loaded")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        print("Joined new server")
        try:
            async with async_session() as session:
                async with session.begin():
                    guild_id = guild.id
                    guild_name = guild.name
                    guild_db = await session.get(GuildModel, guild.id)

                    if not guild_db:
                        new_guild = GuildModel(guild_id=guild_id, name=guild_name)
                        await add_guild(session, new_guild)

                        print(f"Added new guild: {guild.name} ({guild.id})")

            me = guild.me  

            await me.edit(nick="Namu Bot")
            print(f"Nickname set in {guild.name}")

        except Exception as e:
            print(f"Could not change nickname in {guild.name}: {e}")

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        async with async_session() as session:
            async with session.begin():
                db_guild = await session.get(GuildModel, after.id)
                if db_guild and db_guild.name != after.name:
                    db_guild.name = after.name
                    print(f"Updated guild name: {after.name} ({after.id})")


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildCog(bot))