import os
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1514939530833301556

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Синхронизировано: {len(synced)}")
    except Exception as e:
        print(f"Ошибка sync: {e}")

    print(f"Бот запущен как {bot.user}")

@bot.tree.command(name="test", description="Проверка")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("Бот работает!")

@bot.tree.error
async def on_app_command_error(interaction, error):
    print(f"ОШИБКА КОМАНДЫ: {repr(error)}")

bot.run(TOKEN)