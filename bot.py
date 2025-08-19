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

@bot.event
async def on_guild_join(guild):
    me = guild.me  

    try:
        await me.edit(nick="Namu Bot")
        print(f"Nickname set in {guild.name}")
    except Exception as e:
        print(f"Could not change nickname in {guild.name}: {e}")

@bot.event

async def main():
    await bot.load_extension("cogs.translation", extras = {"client": client})

if __name__ == "__main__":
    if not DISCORD_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Missing DISCORD_TOKEN or OPENAI_API_KEY in environment variables")
    bot.run(DISCORD_TOKEN)
    asyncio(main())
