import os
import discord
from discord.ext import commands
from discord import app_commands

from database import init_db, create_player, get_player, add_elo, remove_elo

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1514939530833301556

PLAYER_ROLE = 1514940452980265101
ADMIN_ROLE = 1514939782621433906
OWNER_ROLE = 1514939626903572510

AUTH_CHANNEL = 1514941086420832276
CONFIRM_CHANNEL = 1514941166863388752

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- INIT DB ---------------- #

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

# ---------------- AUTH ---------------- #

@bot.tree.command(name="authorize", description="Авторизация")
async def authorize(interaction: discord.Interaction):

    if interaction.channel.id != AUTH_CHANNEL:
        return await interaction.response.send_message(
            "Используй канал авторизации",
            ephemeral=True
        )

    class Modal(discord.ui.Modal, title="Авторизация"):

        game_id = discord.ui.TextInput(label="Game ID")
        nickname = discord.ui.TextInput(label="Nickname")

        async def on_submit(self, interaction: discord.Interaction):

            create_player(
                str(interaction.user.id),
                self.game_id.value,
                self.nickname.value
            )

            role = interaction.guild.get_role(PLAYER_ROLE)
            if role:
                await interaction.user.add_roles(role)

            channel = bot.get_channel(CONFIRM_CHANNEL)
            if channel:
                await channel.send(f"✅ {interaction.user.mention} зарегистрирован")

            await interaction.response.send_message(
                "Успешно!",
                ephemeral=True
            )

    await interaction.response.send_modal(Modal())

# ---------------- PROFILE ---------------- #

@bot.tree.command(name="profile", description="Профиль")
async def profile(interaction: discord.Interaction):

    user = get_player(str(interaction.user.id))

    if not user:
        return await interaction.response.send_message("Нет профиля", ephemeral=True)

    embed = discord.Embed(title=user[2], color=discord.Color.blue())

    embed.add_field(name="Game ID", value=user[1], inline=False)
    embed.add_field(name="ELO", value=user[3])
    embed.add_field(name="Wins", value=user[4])
    embed.add_field(name="Losses", value=user[5])

    await interaction.response.send_message(embed=embed)

# ---------------- ELO ---------------- #

def is_admin(member: discord.Member):
    return any(r.id in [ADMIN_ROLE, OWNER_ROLE] for r in member.roles)

@bot.tree.command(name="givelo")
async def givelo(interaction: discord.Interaction, member: discord.Member, amount: int):

    if not is_admin(interaction.user):
        return await interaction.response.send_message("Нет прав", ephemeral=True)

    add_elo(str(member.id), amount)

    await interaction.response.send_message(f"+{amount} ELO {member.mention}")


@bot.tree.command(name="ngivelo")
async def ngivelo(interaction: discord.Interaction, member: discord.Member, amount: int):

    if not is_admin(interaction.user):
        return await interaction.response.send_message("Нет прав", ephemeral=True)

    remove_elo(str(member.id), amount)

    await interaction.response.send_message(f"-{amount} ELO {member.mention}")

# ---------------- RUN ---------------- #

bot.run(TOKEN)