import os 
import discord
from discord.ext import commands
from dotenv import load_dotenv 

# Set Up 
intents = discord.Intents.default() 
intents.message_content = True 

# Using commands.bot for more features
# client = discord.Client(intents=intents) 
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    try:
        synced = await bot.tree.sync() 
        print(f"Synced {len(synced)} commands.") 
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="rizz", description="Let me rizz you up shawtty!")
async def rizz(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, world")
 
def main(): 
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN") or ""
    if not token:
        raise Exception("Please add token to .ENV or SECRETS pane.")
    bot.run(token)
    
if __name__ == "__main__":
    main() 