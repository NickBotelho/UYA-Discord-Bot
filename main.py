from discord import player
import requests
import discord
import time
import random
import pymongo
from discord.ext import commands, tasks
from getPlayers import getPlayers, updateOnline
from numPlayers import numPlayers
from getGames import getGames
from callServer import callGames, callPlayers
from getSmokers import getSmokers, pingSmokers, checkTime
from mongodb import Database
from config import botToken
from MapImages import MAP_IMAGES
import os
from StatList import BasicStatList, AdvancedStatList
try:
    if not botToken:
        botToken = os.environ("botToken")
except:
    print('failed to load bot token credentials')
    exit(1)

client = commands.Bot(command_prefix = "!")

onlineCalls, gameCalls, basicStatCalls, advancedStatCalls = 0, 0, 0, 0


player_stats = Database("UYA","Player_Stats")
players_online = Database("UYA","Players_Online")
game_history = Database("UYA", "Game_History")
games_active = Database("UYA","Games_Active")
api_analytics = Database("UYA","API_Analytics")


@client.event
async def on_ready():
    print("Bot is ready...")
    daemon.start()



@client.command()
async def online(ctx):
    global onlineCalls
    onlineCalls+=1


    players = players_online.getOnlinePlayers()
    embed = discord.Embed(
        title = "Players Online",
        # url = "https://socomcommunity.com/servers/10684", 
        # description = "Players Online",
        color=11043122
    )
    field = ""
    for player in players:
        field+='({})\t {}\n'.format(player['status'], player['username'])
    field = "None" if len(field) == 0 else field
    embed.add_field(name ="Aquatos", value = field, inline='False')
    # embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/7/73/Ratchetandclank3box.jpg")
    embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
    await ctx.send(embed = embed)

@client.command()
async def games(ctx):
    global gameCalls
    gameCalls+=1

    games = games_active.getActiveGames()
    embed = discord.Embed(
        title = "Games Active",
        color=11043122
    )

    games_added = 0
    for game in games:
        host = player_stats.getUsername(game['details']['host']) + "'s"
        status = game['details']['status']
        arena = game['details']['map']
        mode = game['details']['gamemode']
        weapons = ""
        for gun in game['details']['weapons']:
            weapons+=gun+",\t"
        
        weapons = "Wrench Only" if weapons == "" else weapons[:len(weapons)-2]

        lobby = ""
        for id in game['details']['players']:
            lobby += player_stats.getUsername(id) + "\t"

        value = """
        Status: {}
        Map: {}
        Gamemode: {}
        Weapons: {}
        Players: {}

        """.format(status, arena, mode, weapons, lobby)
        embed.add_field(name =host, value = value, inline='False')
        if games_added == 0:
            embed.set_thumbnail(url = MAP_IMAGES[arena])
            games_added+=1
    if games_added==0:
        embed.description = "None :("

    await ctx.send(embed =embed)

# @client.command()
# async def total(ctx):
#     info = callPlayers()
#     if info != "error":
#         num = numPlayers(info)
#         await ctx.send("```\n"+num+"```")
#     else:
#         await ctx.send("```\n"+"Failed to communicate with 1up's server"+"```")

# @client.command()
# async def games(ctx):
#     gameInfo = callGames()
#     if gameInfo != "error":
#         games = getGames(gameInfo)
#         await ctx.send("```\n"+games+"```")
#     else:
#         await ctx.send("```\n"+"Failed to communicate with 1up's server"+"```")

# @client.command(pass_context = True)
# async def smoke(ctx):
#     global smokePing
#     global smokeLine
#     global smokeLineDB
#     username = ctx.message.author.name
#     smokePing[username] = ctx.message.author
#     smokeLine[username] = time.time()
#     smokeLineDB.addToSmokeLine(username,ctx.message.author.mention,smokeLine[username])
#     await ctx.send("```\n"+"You have been added to the smoke line.\nYou will automatically be taken out in 30 minutes\n"+"```\n")
    
#     if len(smokeLine) >= 6:
#         await ctx.send("time to smoke {}".format(pingSmokers(smokePing)))
#         smokeLine = {}
#         smokePing = {}
        
# @client.command()
# async def smokers(ctx):
#     global smokePing
#     global smokeLine
#     playersWaiting = getSmokers(smokeLine)
#     await ctx.send("```\n"+playersWaiting+"```")

# @client.command()
# async def playtime(ctx, name):
#     global onlinePlayers
#     global db
#     stored_time = db.getTime(name, onlinePlayers)
#     res = "Player not found. Make sure to enter case sensitive and add quotes if name is two words i.e \"Pooper Scooper\"" if stored_time == None else "{} has played {}".format(name, stored_time)
#     await ctx.send("```\n"+res+"```")

@client.command()
async def basicStats(ctx, username):
    global basicStatCalls
    basicStatCalls+=1
    embed = discord.Embed(
        title = "Basic Stats",
        # url = "https://socomcommunity.com/servers/10684", 
        # description = "Players Online",
        color=11043122
    )
    if player_stats.exists(username):
        info = player_stats.getPlayerBasicStats(username)
        res = ""
        for stat in BasicStatList:
            field = "{}: {}\n".format(stat, info[BasicStatList[stat]])
            res+=field
        embed.add_field(name = '{} Stats'.format(username), value = res)
        embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
        
    else:
        embed.description = "Player not found. Make sure to enter case sensitive and add quotes if name is two words i.e \"Pooper Scooper\". Or you may have to log in to sync your acocunt."
    await ctx.send(embed =embed)

@client.command()
async def advancedStats(ctx, username):
    global advancedStatCalls
    advancedStatCalls+=1
    embed = discord.Embed(
        title = "Advanced Stats",
        # url = "https://socomcommunity.com/servers/10684", 
        # description = "Players Online",
        color=11043122
    )
    if player_stats.exists(username):
        info = player_stats.getPlayerAdvancedStats(username)
        res = ""
        for stat in AdvancedStatList:
            field = "{}: {}\n".format(stat, info[AdvancedStatList[stat]])
            res+=field
        embed.add_field(name = '{} Stats'.format(username), value = res)
        embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
        
    else:
        embed.description = "Player not found. Make sure to enter case sensitive and add quotes if name is two words i.e \"Pooper Scooper\". Or you may have to log in to sync your acocunt."
    await ctx.send(embed =embed)





# @client.command()
# async def biggestSmokers(ctx):
#     global db
#     res = db.getTop10("time_minutes")
#     await ctx.send("```\n"+res+"```")







@tasks.loop(minutes=1.0)
async def daemon():
    global onlineCalls, basicStatCalls, gameCalls, advancedStatCalls
    commands = [onlineCalls, gameCalls, basicStatCalls, advancedStatCalls]
    api_analytics.updateDiscordAnalytics(commands)
    onlineCalls, gameCalls, basicStatCalls, advancedStatCalls = 0, 0, 0, 0










# #lol
# @client.command()
# async def omega_blitzer(ctx):
#     res = ["trop should just be a big cock on the map","rumor has it he doesnt have thumbs",'Did someone say trashcan?', 
#     "what a chump", "ive met bread more intelligent", "oh yah bud?"]
#     out = res[random.randint(0, len(res)-1)]
#     await ctx.send("```\n"+out+"```")






#replace with token
client.run(botToken)