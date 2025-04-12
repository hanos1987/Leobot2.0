import discord
from discord.ext import commands
import json
from ..utility.config_utils import bot_settings
from ..utility.permission_utils import is_mod

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

class TokenManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = load_json('data/tokens.json')

    @commands.command()
    async def givetokens(self, ctx, member: discord.Member, amount: int):
        if not is_mod(ctx.author):
            await ctx.send("Only mods can use this command.")
            return
        user_id = str(member.id)
        self.tokens[user_id] = self.tokens.get(user_id, 0) + amount
        save_json('data/tokens.json', self.tokens)
        await ctx.send(f"Gave {amount} sleep tokens to {member.mention}. They now have {self.tokens[user_id]} tokens.")

    @commands.command()
    async def tokens(self, ctx):
        user_id = str(ctx.author.id)
        amount = self.tokens.get(user_id, 0)
        await ctx.send(f"You have {amount} sleep tokens.")

    def add_tokens(self, user_id, amount):
        self.tokens[str(user_id)] = self.tokens.get(str(user_id), 0) + amount
        save_json('data/tokens.json', self.tokens)

async def setup(bot):
    await bot.add_cog(TokenManager(bot))
