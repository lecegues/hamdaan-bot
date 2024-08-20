import discord 
from discord.ext import commands
from transformers import pipeline

class RizzCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.generator = pipeline('text-generation', model='gpt2')

    def generate_rizz(self):
        prompt = "Write a pickup line sentence."
        response = self.generator(prompt, max_length=100, num_return_sequences=1)
        return response[0]['generated_text'].strip()

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