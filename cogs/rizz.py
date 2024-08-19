import discord 
from discord.ext import commands

class RizzCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 

    @discord.slash_command(name="rizz", description="Let me rizz you up shawtty!")
    async def rizz(self, ctx):
        print("Slash Command: Rizz activated.")
        await ctx.respond("Rizz!!")

    @commands.Cog.listener()
    async def on_member_join(self, member): 
        print("Member has joined the server.")
        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if channel:
            await channel.send("Welcome to the server! 🎉")
        else: 
            print("on_member_join (rizz.py): channel does not exist.")

def setup(bot):
    bot.add_cog(RizzCog(bot))   