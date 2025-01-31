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

        # Prefix Commands Section
        prefix_commands = (
            "`-hello` - Get a friendly greeting\n"
            "`-ping` - Check bot latency\n"
            "`-play <name>` - Play audio file from the audio folder (no extension needed)\n"
            "`-pause` - Pause/resume current audio"
        )
        embed.add_field(
            name="⌨️ Prefix Commands",
            value=f"Prefix: `-`\n{prefix_commands}",
            inline=False
        )

        # Voice Features Section
        voice_features = (
            "• Automatically joins your voice channel when playing audio\n"
            "• Supports .mp3, .wav, .ogg, and .m4a files\n"
            "• Toggle between pause/resume with single command"
        )
        embed.add_field(
            name="🎵 Voice Features",
            value=voice_features,
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

        # Footer with additional info
        embed.set_footer(text="💡 Tip: Slash commands (/) work in DMs and servers!")

        # Send as ephemeral message (only visible to command user)
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )