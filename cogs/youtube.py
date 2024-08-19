import discord 
from discord.ext import commands

class YoutubeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 

    @discord.slash_command(name="youtube", description="Ask me if I have YouTube features!")
    async def youtube(self, ctx):
        print("Slash Command: YouTube activated.")
        await ctx.respond("Not yet! Haha 😂")

def setup(bot):
    bot.add_cog(YoutubeCog(bot))   