import discord

def setup(bot):
    """Setup the help slash command"""
    @bot.tree.command(name="help",description="Get information about available commands and bot features")
    async def help_slash(interaction: discord.Interaction):
        """Show all available commands and features of the bot"""
        
        # Create an embed for better formatting
        embed = discord.Embed(
            title="🍞 BreadBot Help",
            description="Here are all the commands and features available!",
            color=discord.Color.gold()  # Bread-colored!
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
            "`-ping` - Check bot latency"
        )
        embed.add_field(
            name="⌨️ Prefix Commands",
            value=f"Prefix: `-`\n{prefix_commands}",
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
        await interaction.response.send_message(embed=embed,ephemeral=True)