import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utility.config_utils import bot_settings, save_bot_settings

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

BOT_OWNER_ID = 1131932116242939975

# Load cogs
async def load_cogs():
    for filename in os.listdir('leobot/cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'leobot.cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="with Sleep Tokens!"))
    guild = bot.guilds[0]  # Assumes bot is in one guild
    color_roles = bot_settings.get('colorRoles', {})
    for color_name, color_hex in color_roles.items():
        role = discord.utils.get(guild.roles, name=color_name)
        if not role:
            await guild.create_role(name=color_name, color=discord.Color.from_str(color_hex))

# Start bot
async def main():
    await load_cogs()
    await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
