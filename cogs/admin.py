import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import os

# Lade Umgebungsvariablen
load_dotenv('/app/.env')
DISCORD_GUILD_IDS = [int(guild_id.strip()) for guild_id in os.getenv('DISCORD_GUILD_IDS', '').split(',') if guild_id.strip()]

class AdminCommands(commands.Cog):
    """Admin commands for the bot"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="purge",
        description="Löscht Nachrichten im aktuellen Channel"
    )
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in DISCORD_GUILD_IDS])
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

            total_deleted = 0
            batch_size = 50  # Anzahl der Nachrichten pro Batch
            
            if amount is None:
                # Lösche alle Nachrichten in Batches
                while True:
                    deleted = await interaction.channel.purge(limit=batch_size)
                    total_deleted += len(deleted)
                    if len(deleted) < batch_size:
                        break
                    await asyncio.sleep(1)  # Warte 1 Sekunde zwischen den Batches
            else:
                # Lösche die angegebene Anzahl von Nachrichten in Batches
                remaining = amount
                while remaining > 0:
                    current_batch = min(batch_size, remaining)
                    deleted = await interaction.channel.purge(limit=current_batch)
                    total_deleted += len(deleted)
                    remaining -= len(deleted)
                    if len(deleted) < current_batch:
                        break
                    await asyncio.sleep(1)  # Warte 1 Sekunde zwischen den Batches
            
            await interaction.followup.send(
                f"🧹 {total_deleted} Nachrichten wurden gelöscht.",
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
    print("Admin-Commands wurden geladen") 