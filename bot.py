from discord.ext import commands
from openai import OpenAI
from utils.config import load_config
import asyncio
import discord

config = load_config()

OPENAI_API_KEY = config["chat-gpt"]["api-key"]
DISCORD_TOKEN = config["discord"]["token"]


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

client = OpenAI(api_key=OPENAI_API_KEY)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def main():
    bot.openai_client = OpenAI(api_key=OPENAI_API_KEY)

    extensions = [
        "cogs.translation",
        "cogs.guild_cog",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded extension {ext}")
        except Exception as e:
            print(f"Failed to load {ext}: {e}")
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    if not DISCORD_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Missing DISCORD_TOKEN or OPENAI_API_KEY in environment variables")
    
    asyncio.run(main())
