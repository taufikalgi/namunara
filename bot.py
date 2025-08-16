import json
import discord
from discord.ext import commands
from openai import OpenAI

with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

OPENAI_API_KEY = config["chat-gpt"]["api-key"]
DISCORD_TOKEN = config["discord"]["token"]


# Map channel names to target languages
# Example: channel name "english" -> language "English"
# Currently not in use
LANGUAGE_CHANNELS = {
    "english": "English",
    "indonesian": "Indonesian",
    "korean": "Korean"
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

client = OpenAI(api_key=OPENAI_API_KEY)

webhook_cache = {}

translation_map = {
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

    if cache_key in webhook_cache:
        return webhook_cache[cache_key]

    webhooks = await channel.webhooks()
    if webhooks:
        webhook = webhooks[0]
    else:
        webhook = await channel.create_webhook(name="TranslationBot")

    webhook_cache[cache_key] = webhook
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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    src_channel = message.channel.name

    if src_channel in translation_map:
        for target_channel_name, target_lang in translation_map[src_channel]:
            try:
                translated = translate_text(message.content, target_lang)

                webhook = await get_webhook(message.guild, target_channel_name)

                await webhook.send(
                    content=translated,
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url
                )

            except Exception as e:
                print(f"Error translating to {target_channel_name}: {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Missing DISCORD_TOKEN or OPENAI_API_KEY in environment variables")
    bot.run(DISCORD_TOKEN)
