import discord
from discord.ext import commands
import asyncio
from ..utility.config_utils import bot_settings
import json

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

class PlayerCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def changecolor(self, ctx):
        color_roles = bot_settings.get('colorRoles', {})
        colors_list = list(color_roles.keys())
        color_options = "\n".join(f"{i+1}. {name}" for i, name in enumerate(colors_list))
        await ctx.send(f"Choose a color:\n{color_options}\nOr type the color name (case-insensitive):")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            user_input = msg.content.strip().lower()
            
            try:
                selection = int(user_input) - 1
                if 0 <= selection < len(colors_list):
                    selected_color = colors_list[selection]
                else:
                    raise ValueError("Invalid selection number.")
            except ValueError:
                selected_color = next((name for name in colors_list if name.lower() == user_input), None)
                if selected_color is None:
                    raise ValueError("Invalid color name.")
            
            selected_hex = color_roles[selected_color]
            color_role = discord.utils.get(ctx.guild.roles, name=selected_color)
            if not color_role:
                color_role = await ctx.guild.create_role(name=selected_color, color=discord.Color.from_str(selected_hex))
            
            current_color_roles = [role for role in ctx.author.roles if role.name in colors_list]
            for role in current_color_roles:
                await ctx.author.remove_roles(role)
            
            per_user_role_name = str(ctx.author.id)
            per_user_role = discord.utils.get(ctx.guild.roles, name=per_user_role_name)
            if per_user_role:
                await ctx.author.remove_roles(per_user_role)
            
            await ctx.author.add_roles(color_role)
            
            config = load_json('data/config.json')
            config[str(ctx.author.id)] = {"color": selected_hex, "playercard": config.get(str(ctx.author.id), {}).get("playercard", None)}
            save_json('data/config.json', config)
            
            await ctx.send(f"Color updated to {selected_color}! Hex code: {selected_hex}")
        
        except (ValueError, asyncio.TimeoutError):
            await ctx.send("Invalid input or timeout. Color unchanged.")

    @commands.command()
    async def playercard(self, ctx):
        playercard_channel = bot_settings.get('channelIds', {}).get('playerCardChannel')
        if playercard_channel and ctx.channel.id != playercard_channel:
            await ctx.send("This command only works in the player card channel!")
            return
        questions = [
            "Pronouns?", "Zodiac?", "Languages?", "Time Zone?", "Country?", "Occupation?",
            "Favorite Band Member?", "Discover Sleep Token?", "YouTube?", "Fun Facts?",
            "Hobbies?", "Favorite Food?", "Favorite Games?", "Favorite Show?", "Discord Open?"
        ]
        answers = {}
        for q in questions:
            await ctx.author.send(q)
            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=300)
                answers[q] = msg.content
            except asyncio.TimeoutError:
                await ctx.author.send("Timed out. Player card creation cancelled.")
                return
        card = (
            f"**{ctx.author.display_name}'s Player Card**\n\n"
            f"**Pronouns**\n{answers['Pronouns?']}\n"
            f"**Zodiac**\n{answers['Zodiac?']}\n"
            f"**Languages**\n{answers['Languages?']}\n"
            f"**Time Zone**\n{answers['Time Zone?']}\n"
            f"**Country**\n{answers['Country?']}\n"
            f"**Occupation**\n{answers['Occupation?']}\n"
            f"**Favorite Band Member**\n{answers['Favorite Band Member?']}\n"
            f"**Discover Sleep Token**\n{answers['Discover Sleep Token?']}\n"
            f"**YouTube**\n{answers['YouTube?']}\n"
            f"**Fun Facts**\n{answers['Fun Facts?']}\n"
            f"**Hobbies**\n{answers['Hobbies?']}\n"
            f"**Favorite Food**\n{answers['Favorite Food?']}\n"
            f"**Favorite Games**\n{answers['Favorite Games?']}\n"
            f"**Favorite Show**\n{answers['Favorite Show?']}\n"
            f"**Discord Open?**\n{answers['Discord Open?']}\n\n"
            f"Player card created by {ctx.author.mention}"
        )
        config = load_json('data/config.json')
        config[str(ctx.author.id)] = {"color": config.get(str(ctx.author.id), {}).get("color", "#FFFFFF"), "playercard": card}
        save_json('data/config.json', config)
        if playercard_channel:
            channel = self.bot.get_channel(playercard_channel)
            await channel.send(card)
        else:
            await ctx.send(card)

async def setup(bot):
    await bot.add_cog(PlayerCard(bot))
