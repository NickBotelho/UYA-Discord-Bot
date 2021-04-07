import requests
import discord
from discord.ext import tasks
from getPlayers import getPlayers
from numPlayers import numPlayers
from getGames import getGames
from callServer import callGames, callPlayers
import asyncio
import os

client = discord.Client()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

def getText():
    info = callPlayers()
    players = getPlayers(info)

    gameInfo = callGames()
    games = getGames(gameInfo)

    return players + '\n```' + games + '```'

@client.event
async def on_ready():
    print("Bot is ready...")

    channel = client.get_channel(CHANNEL_ID)

	# First message
    text = getText()
    message = await channel.send(getText())

    while True:
        await asyncio.sleep(1)
        await message.edit(content=getText())

client.run(TOKEN)
