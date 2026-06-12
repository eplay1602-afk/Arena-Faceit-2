import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(f"Ошибка sync: {e}")

    print(f"Бот запущен как {bot.user}")

@bot.tree.command(
    name="test",
    description="Проверка работы"
)
async def test(interaction: discord.Interaction):

    await interaction.response.send_message(
        "✅ Бот работает!"
    )

@bot.tree.command(
    name="ping",
    description="Пинг"
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        f"🏓 Pong!"
    )

@bot.tree.error
async def on_app_command_error(interaction, error):

    print("ОШИБКА КОМАНДЫ:")
    print(repr(error))

bot.run(TOKEN)