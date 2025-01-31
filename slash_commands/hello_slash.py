import discord

def setup(bot):
    """Setup the hello slash command"""
    @bot.tree.command(name="hello", description="Get a friendly greeting from the bot")
    async def hello_slash(interaction: discord.Interaction):
        """Slash command version of hello"""
        await interaction.response.send_message(f'Hello! I am {bot.user.name}! 🍞')