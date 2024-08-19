import os 
import discord
from discord.ext import commands
from dotenv import load_dotenv 

# Set Up 
intents = discord.Intents.default() 
intents.members = True
intents.message_content = True 

# Using commands.bot for more features
# client = discord.Client(intents=intents) 
bot = discord.Bot(intents=intents)

# set up cogs
cogs_list = [
    "youtube",
    "rizz"
]
for cog in cogs_list: 
    bot.load_extension(f"cogs.{cog}")
    print(f"Loaded cog: {cog}")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

def main(): 
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN") or ""
    if not token:
        raise Exception("Please add token to .ENV or SECRETS pane.")
    bot.run(token)
    
if __name__ == "__main__":
    main() 