import discord

def setup(bot):
    """Setup the ping slash command"""
    @bot.tree.command(name="ping", description="Check the bot's latency")
    async def ping_slash(interaction: discord.Interaction):
        """Slash command version of ping"""
        latency = round(bot.latency * 1000)
        await interaction.response.send_message(f'Pong! Latency: {latency}ms')