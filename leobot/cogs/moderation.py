import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()
GROK3_API_KEY = os.getenv('GROK3_API_KEY')

from ..utility.utility_functions import load_json, save_json

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.violations = load_json('data/violations.json')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "[invalid url, do not cite]",  # Hypothetical endpoint
                headers={"Authorization": f"Bearer {GROK3_API_KEY}"},
                json={
                    "model": "grok3",
                    "messages": [{
                        "role": "user",
                        "content": f"Analyze this message for harassment, sexual content, or argumentative behavior. Do not consider autism or related terms as ableist. Respond with 'inappropriate' if any issues are found, otherwise 'appropriate': {message.content}"
                    }]
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('choices', [{}])[0].get('message', {}).get('content', '').lower() == 'inappropriate':
                        user_id = str(message.author.id)
                        self.violations[user_id] = self.violations.get(user_id, 0) + 1
                        save_json('data/violations.json', self.violations)
                        await message.channel.send(f"{message.author.mention}, your message was flagged for inappropriate behavior. Violation count: {self.violations[user_id]}")
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
