import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    """Admin commands for the bot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount: int = None):
        """Löscht Nachrichten im aktuellen Channel."""
        if ctx.author.id != self.bot.owner_id:
            await ctx.send("Dieser Command ist nur für den Bot-Owner verfügbar.", ephemeral=True)
            return

        try:
            if amount is None:
                # Lösche alle Nachrichten
                deleted = await ctx.channel.purge(limit=None)
            else:
                # Lösche die angegebene Anzahl von Nachrichten
                deleted = await ctx.channel.purge(limit=amount + 1)  # +1 für den Command selbst
            
            confirmation = await ctx.send(f"🧹 {len(deleted)} Nachrichten wurden gelöscht.")
            await confirmation.delete(delay=5)
        except Exception as e:
            await ctx.send(f"Fehler beim Löschen der Nachrichten: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
    print("Admin-Commands wurden registriert") 