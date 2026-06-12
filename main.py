import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Бот запущен: {bot.user}")
    
    #----REG---#
class RegisterModal(discord.ui.Modal, title="Авторизация"):

    game_id = discord.ui.TextInput(
        label="Игровой ID",
        placeholder="Только цифры"
    )

    nickname = discord.ui.TextInput(
        label="Никнейм",
        placeholder="Ваш игровой ник"
    )

    async def on_submit(self, interaction: discord.Interaction):

        if not self.game_id.value.isdigit():
            await interaction.response.send_message(
                "ID должен содержать только цифры",
                ephemeral=True
            )
            return

        conn = sqlite3.connect("arenafc.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO players
            (discord_id, game_id, nickname)
            VALUES (?, ?, ?)
            """,
            (
                str(interaction.user.id),
                self.game_id.value,
                self.nickname.value
            )
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            "Авторизация успешно завершена!",
            ephemeral=True
        )


@bot.tree.command(name="authorize", description="Авторизация")
async def authorize(interaction: discord.Interaction):
    await interaction.response.send_modal(RegisterModal())
#------PROFILE-----#
@bot.tree.command(name="profile", description="Профиль игрока")
async def profile(interaction: discord.Interaction):

    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE discord_id = ?",
        (str(interaction.user.id),)
    )

    player = cursor.fetchone()

    conn.close()

    if not player:
        await interaction.response.send_message(
            "Сначала пройдите авторизацию",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"Профиль {player[2]}",
        color=discord.Color.blue()
    )

    embed.add_field(name="Игровой ID", value=player[1])
    embed.add_field(name="ELO", value=player[3])
    embed.add_field(name="Победы", value=player[4])
    embed.add_field(name="Поражения", value=player[5])

    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)
    #-----RUN------#
bot.run(TOKEN)