from discord import app_commands
from discord.ext import commands
from models import GuildModel, TranslationChannelModel
from repository.db import async_session
from repository import guild_repository, translation_channel_repository
import discord

class TranslationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.client = bot.openai_client
        self.webhook_cache = {}
        # self.translation_map = {
        #     "en": [("id", "id")],
        #     "id": [("en", "en")],
        #     # "en": [("kr", "kr"), ("id", "id"), ("pl", "pl")],
        #     # "id": [("kr", "kr"), ("en", "en"), ("pl", "pl")],
        #     # "kr": [("en", "en"), ("id", "id"), ("pl", "pl")],
        #     # "pl": [("kr", "kr"), ("id", "id"), ("en", "en")],
        # }

    async def get_webhook(self, guild: discord.Guild, channel_ref):
        if isinstance(channel_ref, discord.TextChannel):
            channel = channel_ref
            channel_name = channel.name
        elif isinstance(channel_ref, str):
            channel = discord.utils.get(guild.text_channels, name=channel_ref)
            if channel is None:
                raise ValueError(f"Channel '{channel_ref}' not found in guild '{guild.name}'.")
            channel_name = channel_ref
        else:
            raise TypeError("channel_ref must be a discord.TextChannel or str")

        cache_key = f"{guild.id}:{channel_name}"

        if cache_key in self.webhook_cache:
            return self.webhook_cache[cache_key]

        webhooks = await channel.webhooks()
        if webhooks:
            webhook = webhooks[0]
        else:
            webhook = await channel.create_webhook(name="TranslationBot")

        self.webhook_cache[cache_key] = webhook
        return webhook
    
    async def get_webhook_by_channel_id(self, guild: discord.Guild, channel_id: int) -> discord.Webhook:
        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel with ID {channel_id} not found in guild {guild.name}")
        
        # cache webhooks
        webhooks = await channel.webhooks()
        if webhooks:
            return webhooks[0]
        
        webhooks = await channel.create_webhook(name="TranslationBot")
        return webhooks

    def translate_text(self, text: str, target_language: str) -> str:
        """
        Use GPT-5-mini for cost-effective translations.
        """
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a translation engine. Translate text into {target_language}. Do not add commentary."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Translation cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.guild and message.guild.id:
            try:
                async with async_session() as session:
                    async with session.begin():
                        allow_translation = await guild_repository.get_guild_allow_translation_by_guild_id(
                            session=session,
                            guild_id=message.guild.id
                        )
                        if not allow_translation:
                            print(f"Guild {message.guild.name} ({message.guild.id}) does not have permission to translate message!")
                            return
                        
            except Exception as e:
                print(f"Guild with id: {message.guild.id} does not exists! {e}")

        src_channel = message.channel.id
        try:
            async with async_session() as session:
                async with session.begin():
                    guild = await guild_repository.get_guild_by_guild_id(
                        session=session,
                        guild_id=message.guild.id
                    )

                    translation_channel_list = await translation_channel_repository.get_translation_channel_by_guild_id(
                        session=session,
                        guild_id=guild.id
                    )
        except Exception as e:
            print(f"Error while fetching translation channels for guild {message.guild.id}: {e}")

        print(translation_channel_list)

        for target_channel in translation_channel_list:
            if target_channel.channel_id == src_channel:
                continue

            try:
                translated = self.translate_text(message.content, target_language=target_channel.language)

                webhook = await self.get_webhook_by_channel_id(message.guild, target_channel.channel_id)

                await webhook.send(
                    content=translated,
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url
                )

            except Exception as e:
                print(f"Error translating to {target_channel.id}: {e}")

        # if src_channel in self.translation_map:
        #     print("Masuk translation map")
        #     for target_channel_name, target_lang in self.translation_map[src_channel]:
        #         try:
        #             translated = self.translate_text(message.content, target_lang)

        #             webhook = await self.get_webhook(message.guild, target_channel_name)

        #             await webhook.send(
        #                 content=translated,
        #                 username=message.author.display_name,
        #                 avatar_url=message.author.display_avatar.url
        #             )

        #         except Exception as e:
        #             print(f"Error translating to {target_channel_name}: {e}")

    @app_commands.command(
        name="add_translation_channel",
        description="Add a channel as a translation channel"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_translation_channel(self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel, 
        language: str
    ):
        async with async_session() as session:
            try:
                guild = await guild_repository.get_guild_by_guild_id(
                    session=session, 
                    guild_id=interaction.guild_id
                )
                if not guild:
                    # not sure if it's better to add it to database or raise custom exception GuildNotFound
                    guild = GuildModel(
                        guild_id=interaction.guild_id,
                        name=interaction.guild.name
                    )
                    await guild_repository.add_guild(guild)
                    await session.flush()

                translation_channel = TranslationChannelModel(
                    channel_id=channel.id,
                    language=language,
                    guild_id=guild.id
                )

                await translation_channel_repository.add_translation_channel(session=session, new_translation_channel=translation_channel)
                await interaction.response.send_message(
                    f"{channel.mention} added as a translation channel for `{language}`"
                )

            except Exception as e:
                await session.rollback()
                await interaction.response.send_message(
                    f"Failed to add channel: {e}",
                    ephemeral=True
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(TranslationCog(bot))