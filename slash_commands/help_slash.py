import discord

def setup(bot):
    """Setup the help slash command"""
    @bot.tree.command(
        name="help",
        description="Get information about available commands and bot features"
    )
    async def help_slash(interaction: discord.Interaction):
        """Show all available commands and features of the bot"""
        
        # Create an embed for better formatting
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
            "`-queue` - Show the current music queue"
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

        # Footer with prefix info
        embed.set_footer(text="Prefix commands use '-' | Slash commands (/) work in DMs and servers!")

        # Send as ephemeral message (only visible to command user)
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )