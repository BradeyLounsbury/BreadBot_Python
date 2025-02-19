import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Import command modules
from prefix_commands import hello, pause, ping, play, queue, skip
from slash_commands import hello_slash, help_slash, ping_slash

# Load environment variables
load_dotenv()

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance with modified prefix
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord"""
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        # await bot.sync_commands()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Setup commands
def setup_commands(bot):
    """Setup all command modules"""
    hello.setup(bot)
    pause.setup(bot)
    ping.setup(bot)
    play.setup(bot)
    queue.setup(bot)
    skip.setup(bot)

    hello_slash.setup(bot)
    ping_slash.setup(bot)
    help_slash.setup(bot)

@bot.event
async def on_message(message):
    """Event triggered when a message is sent in a channel the bot can see"""
    # Don't respond to ourselves
    if message.author == bot.user:
        return

    # Process commands
    await bot.process_commands(message)

    # Custom message responses
    if 'bread' in message.content.lower():
        await message.channel.send('Did someone say bread? 🍞')

# Run the bot
def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No token found! Make sure to set DISCORD_TOKEN in your .env file")
    
    # Setup all commands
    setup_commands(bot)
    
    # Run the bot
    bot.run(token)

if __name__ == "__main__":
    main()