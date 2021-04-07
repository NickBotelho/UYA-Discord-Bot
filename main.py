import requests
import discord
import time
from discord.ext import commands, tasks
from getPlayers import getPlayers
from numPlayers import numPlayers
from getGames import getGames
from callServer import callGames, callPlayers
from getSmokers import getSmokers, pingSmokers, checkTime

client = commands.Bot(command_prefix = "!")

smokeLine = {} #key = user --> time in the line
smokePing = {}#key = user --> their mention for pinging

@client.event
async def on_ready():
    print("Bot is ready...")
    daemon.start()

@client.command()
async def commands(ctx):
    cmd = """!online - lists who is online\n!total - says how many players online\n!games - lists the open games
!smoke - add youself to the smoke line to let others know you want to smoke. Will ping smokers when 6 people want smoke\n!smokers - see who else is waiting to play"""
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

@client.command(pass_context = True)
async def smoke(ctx):
    global smokePing
    global smokeLine
    username = ctx.message.author.name
    smokePing[username] = ctx.message.author
    smokeLine[username] = time.time()
    await ctx.send("```\n"+"You have been added to the smoke line.\nYou will automatically be taken out in 30 minutes\n"+"```\n")
    
    if len(smokeLine) >= 6:
        await ctx.send("time to smoke {}".format(pingSmokers(smokePing)))
        smokeLine = {}
        smokePing = {}
        
@client.command()
async def smokers(ctx):
    global smokePing
    global smokeLine
    playersWaiting = getSmokers(smokeLine)
    await ctx.send("```\n"+playersWaiting+"```")

@tasks.loop(minutes = 5.0)
async def daemon():
    global smokePing
    global smokeLine
    curr = time.time()
    if len(smokeLine) > 0:
        smokeLine = checkTime(smokeLine, curr)
client.run("ODI4ODQyMjY5MzM5NjgwNzY5.YGvdhA.F6Ho7uNMctIs27Xe-dIAdor17wI")