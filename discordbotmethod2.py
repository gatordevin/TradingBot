import discord
import asyncio

TOKEN_AUTH = "MzAyMTc0OTAwNjYyMDQyNjI1.YktqzQ.rfm-XEyLMet3uUXb0YSyHYVlvPU" # Retrieved from browser local storage

client = discord.Client() 

@client.event
async def on_ready():
    pass

@client.event
async def on_message(message : discord.Message):
    print(message.content)

client.run(TOKEN_AUTH, bot=False)