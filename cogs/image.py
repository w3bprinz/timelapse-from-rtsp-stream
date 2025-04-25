import discord
from discord import app_commands
from discord.ext import commands
import glob
import os
import subprocess
from dotenv import load_dotenv

class ImageCommands(commands.Cog):
    """Image commands for the bot"""
    def __init__(self, bot):
        self.bot = bot
        # Lade die Channel-ID aus der .env
        load_dotenv('/app/.env')
        self.daily_channel_id = int(os.getenv('DISCORD_DAILY_CHANNEL_ID'))

    @app_commands.command(name="last", description="Zeigt das letzte aufgenommene Bild")
    @app_commands.guild_only()
    async def last(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            # Hole das letzte Bild
            image_dir = os.getenv('IMAGE_DIR', 'images')
            files = glob.glob(os.path.join(image_dir, '*.jpg'))
            if not files:
                await interaction.followup.send(
                    "Keine Bilder gefunden.",
                    ephemeral=True
                )
                return

            # Sortiere nach Änderungsdatum und nimm das neueste
            latest_file = max(files, key=os.path.getmtime)
            
            # Überprüfe die Dateigröße
            file_size = os.path.getsize(latest_file)
            if file_size > 10 * 1024 * 1024:  # 10MB
                # Verkleinere das Bild
                subprocess.run(['convert', latest_file, '-resize', '50%', latest_file])

            # Sende das Bild
            await interaction.followup.send(
                file=discord.File(latest_file)
            )
        except Exception as e:
            await interaction.followup.send(
                f"Fehler beim Abrufen des letzten Bildes: {str(e)}",
                ephemeral=True
            )

    def resize_image(self, input_file):
        """Verkleinert ein Bild, falls es größer als 10MB ist"""
        max_size_mb = 10
        size_mb = int(subprocess.check_output(['du', '-m', input_file]).split()[0].decode('utf-8'))
        
        if size_mb > max_size_mb:
            print(f"Bild ist zu groß ({size_mb} MB), verkleinere es...")
            # Behalte die ursprüngliche Dateiendung bei
            file_ext = os.path.splitext(input_file)[1]
            temp_file = f"{os.path.splitext(input_file)[0]}_resized{file_ext}"
            
            # Verkleinere das Bild mit ffmpeg
            subprocess.run([
                'ffmpeg', '-y',
                '-i', input_file,
                '-frames:v', '1',
                '-update', '1',
                '-vf', "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease",
                '-compression_level', '9',
                temp_file
            ], check=True)
            
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                return temp_file
            else:
                print("Fehler beim Verkleinern des Bildes")
                return None
        return input_file

async def setup(bot):
    await bot.add_cog(ImageCommands(bot))
    print("Image-Commands wurden registriert") 