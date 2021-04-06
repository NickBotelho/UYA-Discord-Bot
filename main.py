import requests
import discord
from discord.ext import commands
from getPlayers import getPlayers
from numPlayers import numPlayers
from getGames import getGames
from callServer import callGames, callPlayers

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    print("Bot is ready...")

@client.command()
async def commands(ctx):
    cmd = "!online - lists who is online\n"+"!total - says how many players online\n"+"!games - lists the open games\n"
    await ctx.send("```\n"+cmd+"```")

@client.command()
async def online(ctx):
    info = callPlayers()
    players = getPlayers(info)
    await ctx.send("```\n"+players+"```")

@client.command()
async def total(ctx):
    info = callPlayers()
    num = numPlayers(info)
    await ctx.send("```\n"+num+"```")

@client.command()
async def games(ctx):
    gameInfo = callGames()
    games = getGames(gameInfo)
    await ctx.send("```\n"+games+"```")


client.run("ODI4ODQyMjY5MzM5NjgwNzY5.YGvdhA.cSfblOqHXP-Q-P-WJy91T8e--GU")