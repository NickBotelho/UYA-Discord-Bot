from logging import error
from discord import player
import discord
from discord.ext import commands, tasks
from mongodb import Database
from config import BOT_TOKEN, CHAT_CHANNEL, TODAYS_PLAYERS
from MapImages import MAP_IMAGES
import os
from GameChat import getGameChat, updateChatEmbed, updateMessages
from StatList import BasicStatList, AdvancedStatList
from itertools import permutations
from playThread import updatePlayEmbed
# import elo as ELO
from time import strftime, localtime
import time
os.environ['TZ'] = 'EST+05EDT,M4.1.0,M10.5.0'
time.tzset()
try:
    print("Loading Discord information")
    if not BOT_TOKEN:
        BOT_TOKEN = os.environ["BOT_TOKEN"]
    if not CHAT_CHANNEL:
        CHAT_CHANNEL = os.environ['CHAT_CHANNEL']
        CHAT_CHANNEL = int(CHAT_CHANNEL)
    if not TODAYS_PLAYERS:
        TODAYS_PLAYERS = os.environ['TODAYS_PLAYERS']
        TODAYS_PLAYERS = int(TODAYS_PLAYERS)
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
    # global smoke_alerted
    # global smoke_cooldown
    # smoke_cooldown = 0
    # smoke_alerted = False



    chat_channel = client.get_channel(TODAYS_PLAYERS)
    global play_set, daily_reset, updatingPlayChannel, todays_date
    # updatingPlayChannel = chat_channel
    daily_reset = False
    play_set = []
    todays_date = strftime("%a, %b %d", localtime())
    updatingPlayChannel = await chat_channel.send(embed = updatePlayEmbed([], todays_date))
    
    play_channel.start(updatingPlayChannel)
    # global message_stack
    # global message_history
    # message_stack = []
    # message_history = {}
    # chat.start(chat_channel)

    # global elo
    # elo = {}
    # with open("elos.txt", 'r') as file:
    #     for line in file:
    #         line = line.split(',')
    #         name = ''
    #         for i in range(len(line)-1):
    #             if i > 0:
    #                 name = name + ','+line[i]
    #             else:
    #                 name+=line[i]
                
    #         curr_elo = int(line[-1][:len(line[-1])-1])

    #         elo[name] = curr_elo



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
    num_players_online = len(players)
    for player in players:
        field+='({})\t {}\n'.format(player['status'], player['username'])
    field = "None" if len(field) == 0 else field
    if field != "None":
        field+="\n[Total Players: {}]\n".format(num_players_online)
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
# async def teams(ctx, idx):
#     global elo
#     games = games_active.getActiveGames()
#     idx = int(idx)
#     if idx >= len(games):
#         #error
#         pass

#     game = games[idx]
#     lobby = []
#     for id in game['details']['players']:
#             lobby.append(player_stats.getUsername(id))

#     possible_teams = permutations(lobby)
#     best = 100
#     best_teams = None
#     for team in list(possible_teams):
#         elos = ELO.getLobbyElos(elo, team)
#         diff = abs(elos[0] - elos[1])
#         if diff < best:
#             best_teams = team
#             best = diff
    
#     mid = len(lobby)//2
#     red = lobby[:mid]
#     blue = lobby[mid:]
#     confidences = ELO.getExpected(ELO.getTeamElo(elo, red), ELO.getTeamElo(elo, blue))

#     embed = discord.Embed(
#         title = "Balanced Teams",
#         color=11043122
#     )

#     res = "Team: {}: Win Confidence {:.2f}\nTeam: {}: Win Confidence {:.2f}".format(red, confidences[0], blue, confidences[1])
#     embed.description = res
#     await ctx.send(embed =embed)


    
    


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

# import requests
# @client.command()
# async def test(ctx):
#     res = requests.get('http://18.237.169.148:8281/players')
#     res = res.json()
#     players = [player['username'] for player in res]

#     embed = discord.Embed(
#         title = "Players Online",
#         # url = "https://socomcommunity.com/servers/10684", 
#         # description = "Players Online",
#         color=11043122
#     )
#     field = ""
#     for player in players:
#         field+='{}\n'.format(player)
#     field = "None" if len(field) == 0 else field
#     num_players_online = len(players)
#     if field != "None":
#         field += "\n[Total Players: {}]\n".format(num_players_online)
#     embed.add_field(name ="Aquatos", value = field, inline='False')
#     # embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/7/73/Ratchetandclank3box.jpg")
#     embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
#     await ctx.send(embed = embed)


@tasks.loop(minutes=1.0)
async def daemon():
    # global smoke_cooldown
    # SMOKE_THRESHOLD = 4

    # res = requests.get('http://18.237.169.148:8281/players')
    # res = res.json()
    # players = [player['username'] for player in res]
    # num_players_online = len(players)
    # if smoke_cooldown == 0 and num_players_online >= SMOKE_THRESHOLD:
    #     aquatos = client.get_channel(357568581178884108)
    #     ROLE_ID = 902044846787817472

    #     await aquatos.send("*Sniff* *Sniff*... I smell smoke...There are {} people on!!!<@&{}>".format(num_players_online, ROLE_ID))
    #     smoke_cooldown = 120
    # else:
    #     smoke_cooldown = smoke_cooldown - 1 if smoke_cooldown != 0 else smoke_cooldown

    global onlineCalls, basicStatCalls, gameCalls, advancedStatCalls
    commands = [onlineCalls, gameCalls, basicStatCalls, advancedStatCalls]
    api_analytics.updateDiscordAnalytics(commands)
    onlineCalls, gameCalls, basicStatCalls, advancedStatCalls = 0, 0, 0, 0

# @tasks.loop(minutes=0.5)
# async def chat(chat_channel):
#     global message_stack
#     global message_history
#     message_stack = updateMessages(message_stack, message_history)
    
#     if len(message_stack) > 0:
#         await chat_channel.send(embed = updateChatEmbed(message_stack))
#         for message in message_history:
#             message_history[message]+=1
#             if message_history[message] == 21:
#                 del message_history[message]

#         for message in message_stack:
#             message_history[message] = 1
#         message_stack = []

@tasks.loop(minutes=0.5)
async def play_channel(chat_channel):
    global play_set, daily_reset, todays_date
    t = int(strftime("%H", localtime()))
    if t == 5 and not daily_reset:
        play_set = []
        daily_reset = True
        todays_date = strftime("%a, %b %d", localtime())
    elif t != 5 and daily_reset:
        daily_reset = False
    await chat_channel.edit(embed = updatePlayEmbed(play_set, todays_date))
    
@client.command()
async def play(ctx):
    global play_set
    if ctx.message.author.name in play_set:
        await ctx.send("```You're already in there, you addict.```")
    else:
        play_set.append(ctx.message.author.name)
        await ctx.send("```Welcome to tonight's smoke.```")




#replace with token
client.run(BOT_TOKEN)