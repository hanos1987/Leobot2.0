import discord
from discord.ext import commands
import asyncio
from ..utility.config_utils import bot_settings, save_bot_settings

BOT_OWNER_ID = 1131932116242939975

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setupleobot(self, ctx):
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.send("Only the bot owner can run this command.")
            return
        current_playercard = bot_settings.get("channelIds", {}).get("playerCardChannel", "None")
        await ctx.send(f"Enter the channel ID for player card creation (current: {current_playercard}):")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            playercard_channel = int(msg.content)
        except (ValueError, asyncio.TimeoutError):
            await ctx.send("Invalid input or timeout. Using current value.")
            playercard_channel = current_playercard if current_playercard != "None" else None
        current_trivia = bot_settings.get("channelIds", {}).get("triviaChannel", "None")
        await ctx.send(f"Enter the channel ID for trivia commands (current: {current_trivia}):")
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            trivia_channel = int(msg.content)
        except (ValueError, asyncio.TimeoutError):
            await ctx.send("Invalid input or timeout. Using current value.")
            trivia_channel = current_trivia if current_trivia != "None" else None
        current_mod = bot_settings.get("channelIds", {}).get("modChannel", "None")
        await ctx.send(f"Enter the channel ID for mod-only commands (current: {current_mod}):")
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            mod_channel = int(msg.content)
        except (ValueError, asyncio.TimeoutError):
            await ctx.send("Invalid input or timeout. Using current value.")
            mod_channel = current_mod if current_mod != "None" else None
        current_admins = bot_settings.get("admins", [BOT_OWNER_ID])
        await ctx.send(f"Enter admin IDs (comma-separated) (current: {', '.join(map(str, current_admins))}):")
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            admin_ids_input = msg.content.strip()
            if admin_ids_input:
                admin_ids = [int(id.strip()) for id in admin_ids_input.split(',') if id.strip()]
                if BOT_OWNER_ID not in admin_ids:
                    admin_ids.append(BOT_OWNER_ID)
            else:
                admin_ids = current_admins
        except (ValueError, asyncio.TimeoutError):
            await ctx.send("Invalid input or timeout. Using current value.")
            admin_ids = current_admins
        bot_settings.setdefault("channelIds", {})
        bot_settings["channelIds"]["playerCardChannel"] = playercard_channel
        bot_settings["channelIds"]["triviaChannel"] = trivia_channel
        bot_settings["channelIds"]["modChannel"] = mod_channel
        bot_settings["admins"] = admin_ids
        save_bot_settings(bot_settings)
        await ctx.send("Setup complete!")

    @commands.command()
    async def setadmin(self, ctx, admin_ids: str):
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.send("Only the bot owner can run this command.")
            return
        admin_ids_list = [int(id.strip()) for id in admin_ids.split(',') if id.strip()]
        if BOT_OWNER_ID not in admin_ids_list:
            admin_ids_list.append(BOT_OWNER_ID)
        bot_settings["admins"] = admin_ids_list
        save_bot_settings(bot_settings)
        await ctx.send("Admins updated successfully.")

    @commands.command()
    async def setplayercardchannel(self, ctx, channel_id: int):
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.send("Only the bot owner can run this command.")
            return
        bot_settings.setdefault("channelIds", {})
        bot_settings["channelIds"]["playerCardChannel"] = channel_id
        save_bot_settings(bot_settings)
        await ctx.send("Player card channel updated successfully.")

    @commands.command()
    async def settriviachannel(self, ctx, channel_id: int):
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.send("Only the bot owner can run this command.")
            return
        bot_settings.setdefault("channelIds", {})
        bot_settings["channelIds"]["triviaChannel"] = channel_id
        save_bot_settings(bot_settings)
        await ctx.send("Trivia channel updated successfully.")

    @commands.command()
    async def setmodchannel(self, ctx, channel_id: int):
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.send("Only the bot owner can run this command.")
            return
        bot_settings.setdefault("channelIds", {})
        bot_settings["channelIds"]["modChannel"] = channel_id
        save_bot_settings(bot_settings)
        await ctx.send("Mod-only channel updated successfully.")

async def setup(bot):
    await bot.add_cog(Setup(bot))
