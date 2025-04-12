from discord.ext import commands
from utility.config_utils import bot_settings
from utility.permission_utils import is_mod

class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def modcommands(self, ctx):
        if not is_mod(ctx.author):
            await ctx.send("You don't have permission to use this command.")
            return
        mod_channel = bot_settings.get('channelIds', {}).get('modChannel')
        if mod_channel and ctx.channel.id != mod_channel:
            await ctx.send("This command can only be used in the mod-only channel.")
            return
        mod_commands = [
            ("givetokens", "Give sleep tokens to members"),
            ("trivia", "Start a trivia game")
        ]
        message = "Mod Commands:\n" + "\n".join(f"- {cmd}: {desc}" for cmd, desc in mod_commands)
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(ModCommands(bot))
