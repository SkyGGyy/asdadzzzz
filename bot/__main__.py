import os
from discord.ext import commands

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or('--'))

bot.remove_command('help')

bot.load_extension('bot.cogs')

bot.run(DISCORD_TOKEN)
