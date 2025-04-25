import discord
from discord import app_commands
from discord.ext import commands
import glob
import os
import subprocess
from dotenv import load_dotenv

class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.group = app_commands.Group(name="image", description="Bild-bezogene Befehle")
        # Lade die Channel-ID aus der .env
        load_dotenv('/app/.env')
        self.daily_channel_id = int(os.getenv('DISCORD_DAILY_CHANNEL_ID'))
        
        last_cmd = app_commands.Command(
            name="last",
            description="Zeigt das letzte aufgenommene Bild",
            callback=self.last
        )
        last_cmd.guild_only = True
        self.group.add_command(last_cmd)
        bot.tree.add_command(self.group)

    async def last(self, interaction: discord.Interaction):
        # Überprüfe, ob der Command im richtigen Channel verwendet wird
        if interaction.channel_id != self.daily_channel_id:
            await interaction.response.send_message(
                "Dieser Command ist nur im Daily Channel verfügbar.",
                ephemeral=True
            )
            return

        try:
            # Finde das neueste Bild im Screenshot-Verzeichnis
            screenshot_dir = "/app/screenshots"
            list_of_files = glob.glob(f"{screenshot_dir}/screenshot_*.png")
            if not list_of_files:
                await interaction.response.send_message("Keine Screenshots gefunden.", ephemeral=True)
                return

            latest_file = max(list_of_files, key=os.path.getctime)
            
            # Verkleinere das Bild, falls nötig
            resized_file = self.resize_image(latest_file)
            if not resized_file:
                await interaction.response.send_message("Fehler beim Verkleinern des Bildes.", ephemeral=True)
                return
            
            # Sende das Bild
            with open(resized_file, 'rb') as f:
                await interaction.response.send_message(file=discord.File(f))
            print(f"Letztes Bild erfolgreich an Discord gesendet: {resized_file}")
            
            # Lösche die temporäre Datei, falls eine erstellt wurde
            if resized_file != latest_file:
                os.remove(resized_file)
        except Exception as e:
            await interaction.response.send_message(f"Fehler beim Senden des Bildes: {str(e)}", ephemeral=True)
            print(f"Fehler beim Senden des letzten Bildes: {str(e)}")

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