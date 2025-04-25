import discord
from discord import app_commands

class AdminCommands(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="admin", description="Admin-Befehle")
        self.bot = bot

    @app_commands.command(name="purge", description="Löscht alle Nachrichten im aktuellen Channel")
    @app_commands.guild_only()
    async def purge(self, interaction: discord.Interaction):
        # Überprüfe, ob der Benutzer der Bot-Owner ist
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "Dieser Command ist nur für den Bot-Owner verfügbar.",
                ephemeral=True
            )
            return

        try:
            # Sende eine Bestätigungsnachricht
            await interaction.response.send_message(
                "Lösche alle Nachrichten im Channel...",
                ephemeral=True
            )
            
            # Lösche alle Nachrichten im Channel
            deleted = await interaction.channel.purge(limit=None)
            await interaction.followup.send(
                f"Erfolgreich {len(deleted)} Nachrichten gelöscht.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"Fehler beim Löschen der Nachrichten: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    commands = AdminCommands(bot)
    bot.tree.add_command(commands) 