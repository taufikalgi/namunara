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

    async def get_webhook_by_channel_id(
        self, guild: discord.Guild, channel_id: int
    ) -> discord.Webhook:
        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel {channel_id} not found")

        cache_key = f"{guild.id}:{channel_id}"

        if cache_key in self.webhook_cache:
            return self.webhook_cache[cache_key]

        webhooks = await channel.webhooks()
        print(f"Channel {channel_id} has {len(webhooks)} webhooks")
        for wh in webhooks:
            if wh.user == self.bot.user:
                self.webhook_cache[cache_key] = wh
                return wh

        # If none usable, create a new one
        new_webhook = await channel.create_webhook(name="TranslationBot")
        print(
            f"Created new webhook {new_webhook.id} for channel {channel_id}, has_token={new_webhook.token is not None}"
        )

        # self.webhook_cache[cache_key] = new_webhook
        return new_webhook

    def translate_text(self, text: str, target_language: str) -> str:
        """
        Use GPT-5-mini for cost-effective translations.
        """
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a translation engine. Translate text into {target_language}. Do not add commentary.",
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Translation cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print(f"Author: {message.author}, Bot: {message.author.bot}")
        if message.author.bot:
            return

        if message.guild and message.guild.id:
            try:
                async with async_session() as session:
                    async with session.begin():
                        allow_translation = await guild_repository.get_guild_allow_translation_by_guild_id(
                            session=session, guild_id=message.guild.id
                        )
                        if not allow_translation:
                            print(
                                f"Guild {message.guild.name} ({message.guild.id}) does not have permission to translate message!"
                            )
                            return

            except Exception as e:
                print(f"Guild with id: {message.guild.id} does not exists! {e}")

        print(
            f"Processing message from {message.author} in guild {message.guild} ({message.guild.id})"
        )

        src_channel = message.channel.id
        try:
            async with async_session() as session:
                async with session.begin():
                    guild = await guild_repository.get_guild_by_guild_id(
                        session=session, guild_id=message.guild.id
                    )

                    translation_channel_list = await translation_channel_repository.get_translation_channel_by_guild_id(
                        session=session, guild_id=guild.id
                    )
        except Exception as e:
            print(
                f"Error while fetching translation channels for guild {message.guild.id}: {e}"
            )

        print(translation_channel_list)

        print(f"Source channel: {src_channel}")
        for target_channel in translation_channel_list:
            if target_channel.channel_id == src_channel:
                print(f"  -> Skipping (same as source)")
                continue

            print(f"  -> Processing translation to {target_channel.channel_id}")
            try:
                translated = self.translate_text(
                    message.content, target_language=target_channel.language
                )
                print(f"  -> Translated: {translated}")

                webhook = await self.get_webhook_by_channel_id(
                    message.guild, target_channel.channel_id
                )

                print(f"  -> Got webhook: {webhook.id}")
                await webhook.send(
                    content=translated,
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url,
                )

            except Exception as e:
                print(f"Error translating to channel={target_channel.channel_id}: {e}")

    @app_commands.command(
        name="add_translation_channel",
        description="Add a channel as a translation channel",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_translation_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        language: str,
    ):
        async with async_session() as session:
            try:
                guild = await guild_repository.get_guild_by_guild_id(
                    session=session, guild_id=interaction.guild_id
                )
                if not guild:
                    # not sure if it's better to add it to database or raise custom exception GuildNotFound
                    guild = GuildModel(
                        guild_id=interaction.guild_id, name=interaction.guild.name
                    )
                    await guild_repository.add_guild(guild)
                    await session.flush()

                translation_channel = TranslationChannelModel(
                    channel_id=channel.id, language=language, guild_id=guild.id
                )

                await translation_channel_repository.add_translation_channel(
                    session=session, new_translation_channel=translation_channel
                )
                await interaction.response.send_message(
                    f"{channel.mention} added as a translation channel for `{language}`"
                )

            except Exception as e:
                await session.rollback()
                await interaction.response.send_message(
                    f"Failed to add channel: {e}", ephemeral=True
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(TranslationCog(bot))
