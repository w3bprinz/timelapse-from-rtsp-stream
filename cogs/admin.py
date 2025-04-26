import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv('/app/.env')
DISCORD_GUILD_IDS = [int(guild_id.strip()) for guild_id in os.getenv('DISCORD_GUILD_IDS', '').split(',') if guild_id.strip()]

class Admin(commands.Cog):
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

    @app_commands.command(
        name="status",
        description="Zeigt den aktuellen Status des Bots"
    )
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in DISCORD_GUILD_IDS])
    @app_commands.checks.has_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="Bot Status",
            description="Aktuelle Informationen über den Bot",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Bot Name",
            value=self.bot.user.name,
            inline=True
        )
        embed.add_field(
            name="Bot ID",
            value=self.bot.user.id,
            inline=True
        )
        
        embed.add_field(
            name="Server",
            value=interaction.guild.name,
            inline=True
        )
        embed.add_field(
            name="Server ID",
            value=interaction.guild.id,
            inline=True
        )
        
        embed.add_field(
            name="Latenz",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="Umgebungsvariablen",
            value=f"SCREENSHOT_INTERVAL: {os.getenv('SCREENSHOT_INTERVAL', 'Nicht gesetzt')}\n"
                  f"SCREENSHOT_DIR: {os.getenv('SCREENSHOT_DIR', 'Nicht gesetzt')}\n"
                  f"TIMELAPSE_DIR: {os.getenv('TIMELAPSE_DIR', 'Nicht gesetzt')}\n"
                  f"MAX_VIDEO_SIZE_MB: {os.getenv('MAX_VIDEO_SIZE_MB', 'Nicht gesetzt')}",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="restart",
        description="Startet den Bot neu"
    )
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in DISCORD_GUILD_IDS])
    @app_commands.checks.has_permissions(administrator=True)
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await interaction.followup.send("Bot wird neu gestartet...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))
    print("Admin-Commands wurden geladen") 