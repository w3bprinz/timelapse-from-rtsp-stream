import discord
from discord.ext import commands
from discord import app_commands
import os
import glob
from datetime import datetime
import subprocess

class LastImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.screenshot_dir = "/app/screenshots"

    def resize_image(self, input_file):
        """Verkleinert ein Bild, falls es größer als 10MB ist"""
        max_size_mb = 10
        size_mb = int(subprocess.check_output(['du', '-m', input_file]).split()[0].decode('utf-8'))
        
        if size_mb > max_size_mb:
            print(f"Bild ist zu groß ({size_mb} MB), verkleinere es...")
            file_ext = os.path.splitext(input_file)[1]
            temp_file = f"{os.path.splitext(input_file)[0]}_resized{file_ext}"
            
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
        return input_file

    @app_commands.command(
        name="last",
        description="Zeigt das letzte aufgenommene Bild"
    )
    async def last(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            if not os.path.exists(self.screenshot_dir):
                await interaction.followup.send("Der Screenshot-Ordner existiert nicht.", ephemeral=True)
                return

            # Suche nach PNG-Dateien
            list_of_files = glob.glob(os.path.join(self.screenshot_dir, "screenshot_*.png"))
            
            if not list_of_files:
                await interaction.followup.send("Keine Bilder gefunden.", ephemeral=True)
                return

            # Finde die neueste Datei
            latest_file = max(list_of_files, key=os.path.getctime)
            
            # Hole das Erstellungsdatum der Datei
            creation_time = datetime.fromtimestamp(os.path.getctime(latest_file))
            message = f"Letztes Bild vom {creation_time.strftime('%d.%m.%Y %H:%M:%S')}"

            # Verkleinere das Bild falls nötig
            resized_file = self.resize_image(latest_file)

            # Sende das Bild
            with open(resized_file, 'rb') as f:
                await interaction.followup.send(content=message, file=discord.File(f))

            # Lösche temporäre Datei falls erstellt
            if resized_file != latest_file and os.path.exists(resized_file):
                os.remove(resized_file)

        except Exception as e:
            await interaction.followup.send(
                f"Fehler beim Abrufen des letzten Bildes: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(LastImage(bot))
    print("LastImage-Command wurde registriert") 