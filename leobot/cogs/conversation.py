from discord.ext import commands
import openai
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncio  # Added for asynchronous operations

load_dotenv()
OPENAI_API_KEY = os.getenv('GPT4O_API_KEY')
XAI_API_KEY = os.getenv('GROK3_API_KEY')

# Set up OpenAI client for OpenAI API
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Set up OpenAI client for xAI Grok 3 API
xai_client = openai.OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

class Conversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_states = {}  # (user_id, channel_id): [messages]
        self.last_message_time = {}  # (user_id, channel_id): datetime

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
            # Step 1: Use Grok 3 to fetch up-to-date information (DeepSearch should be automatic)
            search_response = xai_client.chat.completions.create(
                model="grok-3-latest",
                messages=[
                    {"role": "system", "content": "You are a research assistant with access to real-time web data. Provide factual, up-to-date information in response to the user's query."},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=200
            )
            search_result = search_response.choices[0].message['content']
            print(f"Grok 3 search result: {search_result}")

            # Step 2: Use OpenAI to generate a conversational response with the search result as context
            conversation_messages = self.conversation_states[key][-10:]
            conversation_messages.append({"role": "system", "content": f"Recent information: {search_result}"})
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_messages,
                max_tokens=100
            )
            reply = response.choices[0].message['content']
            self.conversation_states[key].append({"role": "assistant", "content": reply})
            await message.channel.send(f"{message.author.mention} {reply}")
        except Exception as e:
            await message.channel.send("Sorry, I had an issue responding. Try again!")
            print(f"Error: {e}")
            # Clear conversation state on error to prevent stuck states
            del self.conversation_states[key]
            del self.last_message_time[key]
            await message.channel.send("Conversation ended due to an error.")
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Conversation(bot))
