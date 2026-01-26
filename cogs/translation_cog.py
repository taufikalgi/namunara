from discord import app_commands
from discord.ext import commands
from models import GuildModel, MessageMappingModel, TranslationChannelModel
from repository.db import async_session
from repository import (
    guild_repository,
    message_mapping_repository,
    translation_channel_repository,
)
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

    async def check_is_allowed_to_translate(self, guild: discord.Guild) -> bool:
        try:
            async with async_session() as session:
                async with session.begin():
                    allow_translation = (
                        await guild_repository.get_guild_allow_translation_by_guild_id(
                            session=session, guild_id=guild.id
                        )
                    )
                    if not allow_translation:
                        print(
                            f"Guild {guild.name} ({guild.id}) does not have permission to translate message!"
                        )
                        return False

                    return True

        except Exception as e:
            print(f"Guild with id: {guild.id} does not exists! {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Translation cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print(f"Author: {message.author}, Bot: {message.author.bot}")
        if message.author.bot:
            return

        if message.guild and message.guild.id:
            if not await self.check_is_allowed_to_translate(message.guild):
                return

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

        ref_message = None
        if message.reference is not None:
            print(f" -> Check reference message: {message.reference}")
            ref_message = await message.channel.fetch_message(
                message.reference.message_id
            )
            print(f" -> Referenced message: {ref_message.content}")

        print(translation_channel_list)

        print(f"Source channel: {src_channel}")
        for target_channel in translation_channel_list:
            if target_channel.channel_id == src_channel:
                print(f"  -> Skipping (same as source)")
                continue

            print(f"  -> Processing translation to {target_channel.channel_id}")
            try:
                translated = "place holder translation"
                # translated = self.translate_text(
                #     message.content, target_language=target_channel.language
                # )
                print(f"  -> Translated: {translated}")

                webhook = await self.get_webhook_by_channel_id(
                    message.guild, target_channel.channel_id
                )

                if ref_message is not None:
                    translation_channel_id = (
                        await translation_channel_repository.get_id_by_channel_id(
                            session=session, channel_id=target_channel.channel_id
                        )
                    )
                    translated_ref_message = await message_mapping_repository.get_translated_message_by_original_message_id_and_translation_channel_id(
                        session=session,
                        original_message_id=ref_message.id,
                        translation_channel_id=translation_channel_id,
                    )
                    if (
                        translated_ref_message
                        and translated_ref_message.translated_message_id
                    ):
                        print(
                            f"  -> Found translated reference message id: {translated_ref_message.translated_message_id}"
                        )
                        translated += f"\n\n[In reply to this message](https://discord.com/channels/{message.guild.id}/{target_channel.channel_id}/{translated_ref_message.translated_message_id})"

                print(f"  -> Got webhook: {webhook.id}")
                sent_message = await webhook.send(
                    content=translated,
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url,
                    wait=True,
                )

                async with async_session() as session:
                    async with session.begin():
                        new_mapping = MessageMappingModel(
                            guild_id=message.guild.id,
                            original_message_id=message.id,
                            original_channel_id=message.channel.id,
                            translated_message_id=sent_message.id,
                            translation_channel_id=target_channel.id,
                        )
                        await message_mapping_repository.add_translated_message(
                            session=session,
                            new_mapping=new_mapping,
                        )

            except Exception as e:
                print(f"Error translating to channel={target_channel.channel_id}: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        print(f" On message edit - Author: {after.author}, Bot: {after.author.bot}")
        if before.author.bot or after.author.bot:
            return

        if before.content == after.content:
            return

        print(
            f"Message edited from {before.content} to {after.content} in guild {after.guild} ({after.guild.id})"
        )

        if after.guild and after.guild.id:
            if not await self.check_is_allowed_to_translate(after.guild):
                return

        try:
            async with async_session() as session:
                async with session.begin():
                    mappings = await message_mapping_repository.get_translated_message_by_original_message_id(
                        session=session, original_message_id=before.id
                    )

                    if not mappings:
                        print(
                            f"No translated message found for original message id {before.id}"
                        )
                        return

                    print(
                        f"Found {len(mappings)} mappings for original message id {before.id}"
                    )

                    guild_id = await guild_repository.get_id_by_guild_id(
                        session=session, guild_id=after.guild.id
                    )
                    translation_channel_list = await translation_channel_repository.get_translation_channel_by_guild_id(
                        session=session,
                        guild_id=guild_id,
                    )

                    channel_lang_map = {
                        tc.channel_id: tc.language for tc in translation_channel_list
                    }

        except Exception as e:
            print(f"Error fetching mapping: {e}")
            return

        print(f"  -> Found {len(mappings)} translated messages to update")
        print(mappings)
        print(channel_lang_map)
        for mapping in mappings:
            try:
                target_channel_id = (
                    await translation_channel_repository.get_channel_id_by_id(
                        session=session,
                        id=mapping.translation_channel_id,
                    )
                )
                target_language = channel_lang_map.get(target_channel_id)
                if not target_language:
                    print(
                        f"  -> No language found for channel {target_channel_id}, skipping"
                    )
                    continue

                translated = self.translate_text(
                    after.content, target_language=target_language
                )
                print(f"  -> Translated edited message: {translated}")

                webhook = await self.get_webhook_by_channel_id(
                    after.guild, target_channel_id
                )

                print(f"  -> Got webhook: {webhook.id}")
                await webhook.edit_message(
                    message_id=mapping.translated_message_id,
                    content=translated,
                )
                print(
                    f"  -> Edited translated message id {mapping.translated_message_id} in channel {target_channel_id}"
                )

            except Exception as e:
                print(
                    f"Error updating translated message id {mapping.translated_message_id}: {e}"
                )

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
