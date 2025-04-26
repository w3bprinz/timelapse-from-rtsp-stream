import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

class AdminCommands(commands.Cog):
    """Admin commands for the bot"""
    def __init__(self, bot):
        self.bot = bot
        load_dotenv('/app/.env')
        self.guild_ids = [int(guild_id.strip()) for guild_id in os.getenv('DISCORD_GUILD_IDS', '').split(',') if guild_id.strip()]

    async def cog_load(self) -> None:
        # Registriere den Command direkt im Command-Tree
        @self.bot.tree.command(
            name="purge",
            description="Löscht Nachrichten im aktuellen Channel"
        )
        @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in self.guild_ids])
        @commands.has_permissions(administrator=True)
        async def purge(interaction: discord.Interaction, amount: int = None):
            if interaction.user.id != self.bot.owner_id:
                await interaction.response.send_message(
                    "Dieser Command ist nur für den Bot-Owner verfügbar.",
                    ephemeral=True
                )
                return

            try:
                await interaction.response.defer(ephemeral=True)
                
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
            except Exception as e:
                await interaction.followup.send(
                    f"Fehler beim Löschen der Nachrichten: {str(e)}",
                    ephemeral=True
                )

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
    print("Admin-Commands wurden registriert") 