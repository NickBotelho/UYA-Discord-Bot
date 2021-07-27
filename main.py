from discord import player
import discord
from discord.ext import commands, tasks
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
        realName = player_stats.getRealName(username)
        info = player_stats.getPlayerBasicStats(username)
        res = ""
        for stat in BasicStatList:
            field = "{}: {}\n".format(stat, info[BasicStatList[stat]])
            res+=field
        embed.add_field(name = '{} Stats'.format(realName), value = res)
        embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
        
    else:
        embed.description = "Player not found. Make sure to and add quotes if name is two words i.e \"Pooper Scooper\". Or you may have to log in to sync your acocunt."
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
        realName = player_stats.getRealName(username)
        info = player_stats.getPlayerAdvancedStats(username)
        res = ""
        for stat in AdvancedStatList:
            field = "{}: {}\n".format(stat, info[AdvancedStatList[stat]])
            res+=field
        embed.add_field(name = '{} Stats'.format(realName), value = res)
        embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
        
    else:
        embed.description = "Player not found. Make sure to add quotes if name is two words i.e \"Pooper Scooper\". Or you may have to log in to sync your acocunt."
    await ctx.send(embed =embed)




@tasks.loop(minutes=1.0)
async def daemon():
    global onlineCalls, basicStatCalls, gameCalls, advancedStatCalls
    commands = [onlineCalls, gameCalls, basicStatCalls, advancedStatCalls]
    api_analytics.updateDiscordAnalytics(commands)
    onlineCalls, gameCalls, basicStatCalls, advancedStatCalls = 0, 0, 0, 0




#replace with token
client.run(botToken)