from discord.ext import commands
from datetime import datetime
import pytz

class TimeDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cities = [
            ("Chicago", "America/Chicago"),
            ("New York City", "America/New_York"),
            ("London", "Europe/London"),
            ("Belgium", "Europe/Brussels"),
            ("Moscow", "Europe/Moscow"),
            ("Sydney", "Australia/Sydney"),
            ("Hong Kong", "Asia/Hong_Kong"),
            ("Hawaii", "Pacific/Honolulu"),
            ("Guam", "Pacific/Guam")
        ]

    @commands.command()
    async def time(self, ctx):
        time_str = "Current times:\n"
        for city, tz_str in self.cities:
            tz = pytz.timezone(tz_str)
            current_time = datetime.now(tz).strftime("%H:%M:%S %Z")
            time_str += f"- {city}: {current_time}\n"
        await ctx.send(time_str)

async def setup(bot):
    await bot.add_cog(TimeDisplay(bot))
