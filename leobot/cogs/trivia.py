import discord
from discord.ext import commands
import asyncio
import os
import random
import aiohttp
from html import unescape
from ..utility.utility_functions import load_json, save_json

class Trivia(commands.Cog):
    TRIVIA_CHANNEL_ID = None
    TIMER_DURATION = 25  # Seconds per question
    LEADERBOARD_FILE = "data/trivia_leaderboard.json"
    ROUNDS_FILE = "data/trivia_rounds.json"
    CATEGORY_POOL = [
        "General Knowledge", "Science", "History", "Geography", "Sports",
        "Entertainment", "Literature", "Technology", "Art", "Mathematics"
    ]
    CATEGORY_MAP = {
        "General Knowledge": 9,
        "Entertainment": 11,
        "Science": 17,
        "History": 23,
        "Geography": 22,
        "Sports": 21,
        "Literature": 10,
        "Technology": 18,
        "Art": 25,
        "Mathematics": 19
    }
    DIFFICULTY_MAP = {
        "Easy": "easy",
        "Medium": "medium",
        "Hard": "hard"
    }

    def __init__(self, bot):
        self.bot = bot
        self.is_trivia_active = False
        self.current_question_index = 0
        self.current_question_message = None
        self.timer_task = None
        self.selected_category = None
        self.selected_difficulty = None
        self.question_count = 10
        self.current_questions = []
        self.game_scores = {}
        self.current_guesses = {}
        self.all_time_leaderboard = load_json(self.LEADERBOARD_FILE)
        rounds_data = load_json(self.ROUNDS_FILE)
        self.rounds = rounds_data.get("rounds", 0) if rounds_data else 0
        self.session_token = None
        asyncio.create_task(self.fetch_session_token())

    async def fetch_session_token(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("[invalid url, do not cite]", timeout=5) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    if data["response_code"] == 0:
                        self.session_token = data["token"]
                        return self.session_token
                    return None
        except aiohttp.ClientError:
            return None

    async def fetch_questions(self, category, difficulty):
        category_id = self.CATEGORY_MAP.get(category)
        difficulty_level = self.DIFFICULTY_MAP.get(difficulty)
        if not category_id or not difficulty_level:
            return []
        url = f"[invalid url, do not cite]"
        if self.session_token:
            url += f"&token={self.session_token}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    if data["response_code"] != 0:
                        if data["response_code"] in [3, 4]:
                            self.session_token = await self.fetch_session_token()
                            url = f"[invalid url, do not cite]"
                            async with session.get(url, timeout=5) as resp2:
                                if resp2.status != 200:
                                    return []
                                data = await resp2.json()
                                if data["response_code"] != 0:
                                    return []
                        else:
                            return []
                    questions = []
                    for q in data["results"]:
                        question_text = unescape(q["question"])
                        correct_answer = unescape(q["correct_answer"])
                        incorrect_answers = [unescape(ans) for ans in q["incorrect_answers"]]
                        options = incorrect_answers + [correct_answer]
                        random.shuffle(options)
                        answer_idx = options.index(correct_answer)
                        questions.append({
                            "category": category,
                            "difficulty": difficulty,
                            "question": question_text,
                            "options": options,
                            "answer": answer_idx
                        })
                    return questions
        except aiohttp.ClientError:
            return []

    async def check_trivia_channel(self, ctx):
        from ..utility.config_utils import bot_settings
        trivia_channel = bot_settings.get('channelIds', {}).get('triviaChannel')
        if trivia_channel and ctx.channel.id != trivia_channel:
            await ctx.send(f"Trivia commands are only allowed in <#{trivia_channel}>!")
            return False
        return True

    async def run_poll(self, ctx, message_content, options):
        poll_message = await ctx.send(
            f"{message_content}\n"
            f"🇦: {options[0]}\n"
            f"🇧: {options[1]}\n"
            f"🇨: {options[2]}\n"
            "Poll closes in 10 seconds!"
        )
        for emoji in ['🇦', '🇧', '🇨']:
            await poll_message.add_reaction(emoji)
        await asyncio.sleep(10)
        poll_message = await ctx.channel.fetch_message(poll_message.id)
        reaction_counts = {emoji: 0 for emoji in ['🇦', '🇧', '🇨']}
        for reaction in poll_message.reactions:
            if reaction.emoji in reaction_counts:
                reaction_counts[reaction.emoji] = reaction.count - 1
        max_votes = max(reaction_counts.values())
        if max_votes == 0:
            await ctx.send(f"No votes received, defaulting to: **{options[0]}**")
            return options[0]
        tied_emojis = [emoji for emoji, count in reaction_counts.items() if count == max_votes]
        winning_emoji = random.choice(tied_emojis)
        return options[{'🇦': 0, '🇧': 1, '🇨': 2}[winning_emoji]]

    @commands.command()
    async def trivia(self, ctx):
        from ..utility.permission_utils import is_mod
        if not await self.check_trivia_channel(ctx) or not is_mod(ctx.author):
            return
        if self.is_trivia_active:
            await ctx.send("A trivia game is already in progress!")
            return
        categories = random.sample(self.CATEGORY_POOL, 3)
        self.selected_category = await self.run_poll(
            ctx, "Choose a category:", categories
        )
        await ctx.send(f"Selected category: **{self.selected_category}**")
        difficulties = ["Easy", "Medium", "Hard"]
        self.selected_difficulty = await self.run_poll(
            ctx, "Choose the difficulty:", difficulties
        )
        await ctx.send(f"Selected difficulty: **{self.selected_difficulty}**")
        self.is_trivia_active = True
        questions = await self.fetch_questions(self.selected_category, self.selected_difficulty)
        if questions:
            self.current_questions = questions[:10]
            self.current_question_index = 0
            await self.send_question(ctx.channel)
        else:
            self.is_trivia_active = False
            await ctx.send("Unable to fetch questions. Try again later.")

    async def send_question(self, channel):
        if self.current_question_index >= len(self.current_questions):
            await self.end_game(channel)
            return
        question_data = self.current_questions[self.current_question_index]
        answer_text = "\n".join([f"{chr(65 + i)}: {opt}" for i, opt in enumerate(question_data["options"])])
        self.current_question_message = await channel.send(
            f"Question {self.current_question_index + 1}/{len(self.current_questions)}: {question_data['question']}\n\n{answer_text}\n\n"
            f"React with 🇦, 🇧, 🇨, or 🇩! Time: {self.TIMER_DURATION} seconds."
        )
        for emoji in ['🇦', '🇧', '🇨', '🇩']:
            await self.current_question_message.add_reaction(emoji)
        self.current_guesses[self.current_question_index] = {}
        self.timer_task = asyncio.create_task(self.timer(channel, question_data))

    async def timer(self, channel, question_data):
        await asyncio.sleep(self.TIMER_DURATION)
        guesses = self.current_guesses.get(self.current_question_index, {})
        correct_answer = question_data["options"][question_data["answer"]]
        correct_letter = chr(65 + question_data["answer"])
        correct_users = []
        for user_id, guess in guesses.items():
            if guess == correct_letter:
                self.game_scores[user_id] = self.game_scores.get(user_id, 0) + 1
                user = self.bot.get_user(user_id)
                if user:
                    correct_users.append(user.mention)
        result = f"Time’s up! Correct answer: {correct_answer} (Option {correct_letter})\n"
        if correct_users:
            result += f"Correct: {', '.join(correct_users)}"
        else:
            result += "No one got it right!"
        await channel.send(result)
        self.current_question_index += 1
        await self.send_question(channel)

    async def end_game(self, channel):
        for user_id, score in self.game_scores.items():
            self.all_time_leaderboard[str(user_id)] = self.all_time_leaderboard.get(str(user_id), 0) + score
        save_json(self.LEADERBOARD_FILE, self.all_time_leaderboard)
        self.rounds += 1
        save_json(self.ROUNDS_FILE, {"rounds": self.rounds})
        game_leaderboard = sorted(self.game_scores.items(), key=lambda x: x[1], reverse=True)
        game_text = "Game Leaderboard:\n" + "\n".join(
            [f"{self.bot.get_user(user_id).mention}: {score}" for user_id, score in game_leaderboard]
        ) if game_leaderboard else "No scores this game."
        all_time_leaderboard = sorted(self.all_time_leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
        all_time_text = "All-Time Leaderboard (Top 5):\n" + "\n".join(
            [f"{self.bot.get_user(int(user_id)).mention}: {score}" for user_id, score in all_time_leaderboard]
        ) if all_time_leaderboard else "No scores yet."
        token_cog = self.bot.get_cog("TokenManager")
        token_text = ""
        if token_cog:
            for user_id, score in self.game_scores.items():
                if score > 0:
                    token_cog.add_tokens(user_id, score)
                    user = self.bot.get_user(user_id)
                    if user:
                        token_text += f"Awarded {score} Sleep Token{'s' if score > 1 else ''} to {user.mention}!\n"
        await channel.send(f"Trivia ended!\n\n{game_text}\n\n{all_time_text}" + (f"\n\n{token_text}" if token_text else ""))
        self.is_trivia_active = False
        self.game_scores = {}
        self.current_guesses = {}
        self.selected_category = None
        self.selected_difficulty = None
        self.current_question_message = None
        self.current_questions = []

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user or not self.is_trivia_active or reaction.message != self.current_question_message:
            return
        if reaction.emoji not in ['🇦', '🇧', '🇨', '🇩']:
            return
        letter = {'🇦': 'A', '🇧': 'B', '🇨': 'C', '🇩': 'D'}[reaction.emoji]
        self.current_guesses[self.current_question_index][user.id] = letter
        await reaction.remove(user)

async def setup(bot):
    await bot.add_cog(Trivia(bot))
