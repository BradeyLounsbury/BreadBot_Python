import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Import command modules
from prefix_commands import hello, pause, ping, play, queue, remove, skip, stop
from slash_commands import hello_slash, help_slash, ping_slash

# Load environment variables
load_dotenv()

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance with modified prefix
bot = commands.Bot(command_prefix='-', intents=intents)

def create_help_embed():
    """Create the help message embed"""
    embed = discord.Embed(
        title="🍞 BreadBot Help",
        description="Here are all the commands and features available!",
        color=0x89CFF0  # BreadBot's primary color (baby blue)
    )

    # Slash Commands Section
    slash_commands = (
        "`/hello` - Get a friendly greeting from BreadBot\n"
        "`/ping` - Check the bot's current latency\n"
        "`/help` - Show this help message"
    )
    embed.add_field(
        name="📱 Slash Commands",
        value=slash_commands,
        inline=False
    )

    # Music Commands Section
    music_commands = (
        "`-play <query>` - Play a song from YouTube or local audio file\n"
        "`-pause` - Pause/resume the current song\n"
        "`-skip` - Skip to the next song in queue\n"
        "`-stop` - Stop playing, clear queue, and disconnect\n"
        "`-queue` - Show the current music queue\n"
        "`-remove <position>` or `-r <position>` - Remove a song from queue by position number\n`-rl` - Remove the last song in queue\n"
    )
    embed.add_field(
        name="🎵 Music Commands",
        value=music_commands,
        inline=False
    )

    # General Commands Section
    general_commands = (
        "`-hello` - Get a friendly greeting\n"
        "`-ping` - Check bot latency"
    )
    embed.add_field(
        name="⚡ General Commands",
        value=general_commands,
        inline=False
    )

    # Music Features Section
    music_features = (
        "• Play music from YouTube or local audio files\n"
        "• Queue system for multiple songs\n"
        "• Progress bar with current song position\n"
        "• Supports streaming and local playback\n"
        "• Supports .mp3, .wav, .ogg, and .m4a files\n"
        "• Duration tracking and formatted timestamps"
    )
    embed.add_field(
        name="🎹 Music Features",
        value=music_features,
        inline=False
    )

    # Auto-responses Section
    auto_responses = (
        "• Responds with '🍞' when someone mentions 'bread'"
    )
    embed.add_field(
        name="🤖 Auto-Responses",
        value=auto_responses,
        inline=False
    )

    # Footer with prefix info and last updated timestamp
    embed.set_footer(text="Prefix commands use '-' | Slash commands (/) work in DMs and servers! | Last updated: " + 
                    discord.utils.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
    
    return embed

async def update_help_message():
    """Update or create the help message in the specified channel"""
    # Get the help channel ID from environment variables
    help_channel_id = os.getenv('HELP_CHANNEL_ID')
    
    # If no help channel is configured, return
    if not help_channel_id:
        print("No HELP_CHANNEL_ID configured in .env file. Skipping help message update.")
        return
    
    try:
        # Convert to integer
        help_channel_id = int(help_channel_id)
        
        # Get the channel
        channel = bot.get_channel(help_channel_id)
        
        if not channel:
            print(f"Could not find channel with ID {help_channel_id}")
            return
        
        # Create the help embed
        help_embed = create_help_embed()
        
        # Check for existing pinned messages
        pinned_messages = await channel.pins()
        help_message = None
        
        # Look for a pinned message from the bot that has "BreadBot Help" in the title
        for msg in pinned_messages:
            if msg.author == bot.user and msg.embeds and len(msg.embeds) > 0 and "BreadBot Help" in msg.embeds[0].title:
                help_message = msg
                break
        
        if help_message:
            # Update existing message
            await help_message.edit(embed=help_embed)
            print(f"Updated pinned help message in #{channel.name}")
        else:
            # Create new message
            new_message = await channel.send(embed=help_embed)
            # Pin the message
            await new_message.pin()
            print(f"Created and pinned new help message in #{channel.name}")
            
            # Send additional instructions for the first time
            await channel.send("📌 The help message has been pinned above! It will automatically update when new features are added.")
    
    except Exception as e:
        print(f"Error updating help message: {e}")

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord"""
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        
        # Update the help message
        await update_help_message()
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
    remove.setup(bot)
    skip.setup(bot)
    stop.setup(bot)

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