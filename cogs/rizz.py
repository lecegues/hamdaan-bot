import discord 
from discord.ext import commands
import csv 
import random

RIZZ_FILE_PATH = "static/brainrot_pickup_lines.csv"

class RizzCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.rizz_file = self.load_csv(RIZZ_FILE_PATH)

    def load_csv(self, filepath):
        with open(filepath, mode='r', encoding='utf-8') as file: 
            reader = csv.reader(file)
            return [row[0] for row in reader]

    def generate_rizz(self):
        return random.choice(self.rizz_file)

    @discord.slash_command(name="rizz", description="Let me rizz you up shawtty!")
    async def rizz(self, ctx):
        print("Slash Command: Rizz activated.")
        await ctx.defer()
        rizz_text = self.generate_rizz()
        await ctx.respond(rizz_text)

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