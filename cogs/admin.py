import discord
from discord.ext import commands
from discord import app_commands

class AdminCommands(commands.Cog):
    """Admin commands for the bot"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="purge",
        description="Löscht Nachrichten im aktuellen Channel"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def purge(self, interaction: discord.Interaction, amount: int = None):
        try:
            await interaction.response.defer(ephemeral=True)
            
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    "Du benötigst Administrator-Rechte für diesen Befehl.",
                    ephemeral=True
                )
                return

            if amount is None:
                # Lösche alle Nachrichten
                deleted = await interaction.channel.purge(limit=None)
            else:
                # Lösche die angegebene Anzahl von Nachrichten
                deleted = await interaction.channel.purge(limit=amount)
            
            await interaction.followup.send(
                f"🧹 {len(deleted)} Nachrichten wurden gelöscht.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "Ich habe keine Berechtigung, Nachrichten zu löschen.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"Fehler beim Löschen der Nachrichten: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
    print("Admin-Commands wurden registriert") 