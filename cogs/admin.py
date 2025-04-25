import discord
from discord import app_commands
from discord.ext import commands

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(self.purge)

    @app_commands.command(
        name="purge",
        description="Löscht alle Nachrichten im aktuellen Channel"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
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

    @purge.error
    async def purge_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "Du benötigst Administrator-Rechte für diesen Befehl.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AdminCog(bot)) 