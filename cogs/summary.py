import discord
from discord.ext import commands
import aiohttp
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
GROK3_API_KEY = os.getenv('GROK3_API_KEY')

class Summary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def summary(self, ctx, minutes: int):
        if minutes <= 0:
            await ctx.send("Please specify a positive number of minutes.")
            return
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)
        messages = []
        async for msg in ctx.channel.history(limit=100, after=start_time):
            if not msg.author.bot:
                messages.append(msg.content)
        if not messages:
            await ctx.send("No messages found in the specified time frame.")
            return
        prompt = "Summarize the following conversation briefly, focusing on hot topics discussed. Do not list user names:\n" + "\n".join(messages)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.xai.com/grok3",  # Hypothetical endpoint
                headers={"Authorization": f"Bearer {GROK3_API_KEY}"},
                json={
                    "model": "grok3",
                    "messages": [{"role": "user", "content": prompt}]
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    summary = data.get('choices', [{}])[0].get('message', {}).get('content', 'No summary available.')
                    await ctx.send(f"Summary of the last {minutes} minutes:\n{summary}")
                else:
                    await ctx.send("Failed to generate summary. Try again later.")

async def setup(bot):
    await bot.add_cog(Summary(bot))
