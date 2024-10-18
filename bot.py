# bot.py
import discord
from discord.ext import commands
from config import DISCORD_TOKEN, logger
from database import init_database
from cogs.sydneybot_cog import SydneyBotCog

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True  # Required to read message content
intents.dm_messages = True

# Initialize the bot with a general command prefix
bot = commands.Bot(command_prefix='s!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("------")
    init_database()
    await bot.add_cog(SydneyBotCog(bot))
    logger.info("SydneyBot is ready and operational.")

if __name__ == '__main__':
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start the bot: {e}")