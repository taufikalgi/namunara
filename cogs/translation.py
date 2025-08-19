from discord.ext import commands
from openai import OpenAI
import discord

class Translation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.webhook_cache = {}
        self.translation_map = {
            "en": [("kr", "kr"), ("id", "id"), ("pl", "pl")],
            "id": [("kr", "kr"), ("en", "en"), ("pl", "pl")],
            "kr": [("en", "en"), ("id", "id"), ("pl", "pl")],
            "pl": [("kr", "kr"), ("id", "id"), ("en", "en")],
        }

    async def get_webhook(guild: discord.Guild, channel_ref):
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

    def translate_text(text: str, target_language: str) -> str:
        """
        Use GPT-5-mini for cost-effective translations.
        """
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a translation engine. Translate text into {target_language}. Do not add commentary."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        src_channel = message.channel.name

        if src_channel in self.translation_map:
            for target_channel_name, target_lang in self.translation_map[src_channel]:
                try:
                    translated = self.translate_text(message.content, target_lang)

                    webhook = await self.get_webhook(message.guild, target_channel_name)

                    await webhook.send(
                        content=translated,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar.url
                    )

                except Exception as e:
                    print(f"Error translating to {target_channel_name}: {e}")


async def setup(bot: commands.Bot, client: OpenAI):
    await bot.add_cog(Translation(bot, client))