import os
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1514939530833301556

PLAYER_ROLE = 1514940452980265101
ADMIN_ROLE = 1514939782621433906
OWNER_ROLE = 1514939626903572510

AUTH_CHANNEL = 1514941086420832276
CONFIRM_CHANNEL = 1514941166863388752

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        discord_id TEXT PRIMARY KEY,
        game_id TEXT,
        nickname TEXT,
        elo INTEGER DEFAULT 1000,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- READY ---------------- #

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано: {len(synced)}")
    except Exception as e:
        print(e)

    print(f"Бот запущен как {bot.user}")

    # сообщение в канал авторизации
    channel = bot.get_channel(AUTH_CHANNEL)
    if channel:
        await channel.send(
            "🔐 **Arena FC**\n\nНажмите /authorize для регистрации."
        )

# ---------------- AUTHORIZE ---------------- #

@bot.tree.command(name="authorize", description="Авторизация")
async def authorize(interaction: discord.Interaction):

    if interaction.channel.id != AUTH_CHANNEL:
        await interaction.response.send_message(
            "Используй канал авторизации",
            ephemeral=True
        )
        return

    class AuthModal(discord.ui.Modal, title="Авторизация"):

        game_id = discord.ui.TextInput(label="Game ID")
        nickname = discord.ui.TextInput(label="Nickname")

        async def on_submit(self, interaction: discord.Interaction):

            conn = sqlite3.connect("arenafc.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT OR REPLACE INTO players
            (discord_id, game_id, nickname)
            VALUES (?, ?, ?)
            """, (
                str(interaction.user.id),
                self.game_id.value,
                self.nickname.value
            ))

            conn.commit()
            conn.close()

            role = interaction.guild.get_role(PLAYER_ROLE)
            if role:
                await interaction.user.add_roles(role)

            confirm = bot.get_channel(CONFIRM_CHANNEL)
            if confirm:
                await confirm.send(
                    f"✅ {interaction.user.mention} зарегистрирован"
                )

            await interaction.response.send_message(
                "Успешно зарегистрирован!",
                ephemeral=True
            )

    await interaction.response.send_modal(AuthModal())

# ---------------- PROFILE ---------------- #

@bot.tree.command(name="profile", description="Профиль")
async def profile(interaction: discord.Interaction):

    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE discord_id=?",
                   (str(interaction.user.id),))

    user = cursor.fetchone()
    conn.close()

    if not user:
        await interaction.response.send_message("Нет профиля", ephemeral=True)
        return

    embed = discord.Embed(title=user[2], color=discord.Color.blue())
    embed.add_field(name="Game ID", value=user[1])
    embed.add_field(name="ELO", value=user[3])
    embed.add_field(name="Wins", value=user[4])
    embed.add_field(name="Losses", value=user[5])

    await interaction.response.send_message(embed=embed)

# ---------------- ELO ---------------- #

def check_admin(user: discord.Member):
    return any(r.id in [ADMIN_ROLE, OWNER_ROLE] for r in user.roles)

@bot.tree.command(name="givelo")
@app_commands.describe(user="Игрок", amount="ELO")
async def givelo(interaction: discord.Interaction, user: discord.Member, amount: int):

    if not check_admin(interaction.user):
        return await interaction.response.send_message("Нет прав", ephemeral=True)

    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE players SET elo = elo + ? WHERE discord_id=?",
                   (amount, str(user.id)))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"+{amount} ELO {user.mention}")

@bot.tree.command(name="ngivelo")
async def ngivelo(interaction: discord.Interaction, user: discord.Member, amount: int):

    if not check_admin(interaction.user):
        return await interaction.response.send_message("Нет прав", ephemeral=True)

    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE players SET elo = elo - ? WHERE discord_id=?",
                   (amount, str(user.id)))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"-{amount} ELO {user.mention}")

# ---------------- RUN ---------------- #

bot.run(TOKEN)