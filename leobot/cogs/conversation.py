import asyncio
from discord.ext import commands
import openai
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
GPT_API_KEY = os.getenv('GPT4O_API_KEY')

class Conversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_states = {}  # (user_id, channel_id): [messages]
        self.last_message_time = {}  # (user_id, channel_id): datetime
        openai.api_key = GPT_API_KEY

    async def check_timeout(self):
        while True:
            current_time = datetime.utcnow()
            for key in list(self.conversation_states.keys()):
                if key in self.last_message_time:
                    if current_time - self.last_message_time[key] > timedelta(minutes=5):
                        user_id, channel_id = key
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            await channel.send(f"<@{user_id}>, conversation ended due to inactivity.")
                        del self.conversation_states[key]
                        del self.last_message_time[key]
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.check_timeout())

    @commands.command()
    async def conversation(self, ctx):
        key = (ctx.author.id, ctx.channel.id)
        if key in self.conversation_states:
            await ctx.send("You're already in a conversation in this channel!")
            return
        self.conversation_states[key] = []
        self.last_message_time[key] = datetime.utcnow()
        await ctx.send(f"{ctx.author.mention}, conversation started! Type your messages, and I'll respond.")

    @commands.command()
    async def end_conversation(self, ctx):
        key = (ctx.author.id, ctx.channel.id)
        if key not in self.conversation_states:
            await ctx.send("No active conversation in this channel.")
            return
        del self.conversation_states[key]
        del self.last_message_time[key]
        await ctx.send("Conversation ended.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        key = (message.author.id, message.channel.id)
        if key not in self.conversation_states:
            return
        self.conversation_states[key].append({"role": "user", "content": message.content})
        self.last_message_time[key] = datetime.utcnow()
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=self.conversation_states[key][-10:],  # Limit context
                max_tokens=100  # Keep responses concise
            )
            reply = response.choices[0].message.content
            self.conversation_states[key].append({"role": "assistant", "content": reply})
            await message.channel.send(f"{message.author.mention} {reply}")
        except Exception as e:
            await message.channel.send("Sorry, I had an issue responding. Try again!")
            print(f"GPT error: {e}")
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Conversation(bot))
