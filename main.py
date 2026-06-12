import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1514939530833301556

OWNER_ROLE = 1514939626903572510
ADMIN_ROLE = 1514939782621433906
MOD_ROLE = 1514940013044039791
PLAYER_ROLE = 1514940452980265101

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("arenafc.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    discord_id TEXT PRIMARY KEY,
    game_id TEXT NOT NULL,
    nickname TEXT NOT NULL,
    elo INTEGER DEFAULT 1000,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

# ---------------- READY ---------------- #

@bot.event
async def on_ready():

    guild = discord.Object(id=GUILD_ID)

    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(e)

    print(f"Бот запущен как {bot.user}")
    
conn = sqlite3.connect("arenafc.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master")

print(cursor.fetchall())

conn.close()

# ---------------- REGISTER ---------------- #

class RegisterModal(discord.ui.Modal, title="Авторизация"):

    game_id = discord.ui.TextInput(
        label="Игровой ID",
        placeholder="Только цифры"
    )

    nickname = discord.ui.TextInput(
        label="Никнейм",
        placeholder="Введите игровой ник"
    )

    async def on_submit(self, interaction: discord.Interaction):

        if not self.game_id.value.isdigit():

            await interaction.response.send_message(
                "❌ Игровой ID должен содержать только цифры.",
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

        role = interaction.guild.get_role(PLAYER_ROLE)

        if role:
            await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Авторизация успешно завершена!",
            ephemeral=True
        )

@bot.tree.command(
    name="authorize",
    description="Авторизация",
    guild=discord.Object(id=GUILD_ID)
)
async def authorize(interaction: discord.Interaction):

    await interaction.response.send_modal(
        RegisterModal()
    )

# ---------------- PROFILE ---------------- #

@bot.tree.command(
    name="profile",
    description="Профиль игрока",
    guild=discord.Object(id=GUILD_ID)
)
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
            "❌ Сначала пройдите авторизацию.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"Профиль {player[2]}",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Игровой ID",
        value=player[1],
        inline=False
    )

    embed.add_field(
        name="ELO",
        value=player[3],
        inline=True
    )

    embed.add_field(
        name="Победы",
        value=player[4],
        inline=True
    )

    embed.add_field(
        name="Поражения",
        value=player[5],
        inline=True
    )

    embed.set_thumbnail(
        url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(
        embed=embed
    )

# ---------------- GIVE ELO ---------------- #

@bot.tree.command(
    name="givelo",
    description="Выдать ELO",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    member="Игрок",
    amount="Количество ELO"
)
async def givelo(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int
):

    roles = [r.id for r in interaction.user.roles]

    if OWNER_ROLE not in roles and ADMIN_ROLE not in roles:

        await interaction.response.send_message(
            "❌ Нет прав.",
            ephemeral=True
        )
        return

    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE players
        SET elo = elo + ?
        WHERE discord_id = ?
        """,
        (
            amount,
            str(member.id)
        )
    )

    conn.commit()
    conn.close()

    await interaction.response.send_message(
        f"✅ {member.mention} получил {amount} ELO"
    )

# ---------------- REMOVE ELO ---------------- #

@bot.tree.command(
    name="ngivelo",
    description="Снять ELO",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    member="Игрок",
    amount="Количество ELO"
)
async def ngivelo(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int
):

    roles = [r.id for r in interaction.user.roles]

    if OWNER_ROLE not in roles and ADMIN_ROLE not in roles:

        await interaction.response.send_message(
            "❌ Нет прав.",
            ephemeral=True
        )
        return

    conn = sqlite3.connect("arenafc.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE players
        SET elo = elo - ?
        WHERE discord_id = ?
        """,
        (
            amount,
            str(member.id)
        )
    )

    conn.commit()
    conn.close()

    await interaction.response.send_message(
        f"✅ У {member.mention} снято {amount} ELO"
    )
@bot.tree.error
async def on_app_command_error(interaction, error):
    print(f"ОШИБКА КОМАНДЫ: {error}")
# ---------------- START ---------------- #

bot.run(TOKEN)