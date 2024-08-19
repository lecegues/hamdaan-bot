import os 
import discord
from dotenv import load_dotenv 

intents = discord.Intents.default() 
intents.message_content = True 

client = discord.Client(intents=intents) 

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): 
    if message.author == client.user:
        return 
    
    if message.content.startswith("Hello"):
        await message.channel.send("What's up")
 
def main(): 
    
    try:
        load_dotenv() # if using python-env
        token = os.getenv("DISCORD_TOKEN") or ""
        if token == "":
            raise Exception("Please add token to .ENV or SECRETS pane.")
        client.run(token)
    except discord.HTTPException as e:
        if e.status == 429: 
            print("The Discord servers denied the connection for making too many requests")
            print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
        else: 
            raise e
    
if __name__ == "__main__":
    main() 