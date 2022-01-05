from logging import error
from discord import player
import discord
from discord.ext import commands, tasks
from mongodb import Database
from config import BOT_TOKEN, CHAT_CHANNEL, ONLINE_CHANNEL, TODAYS_PLAYERS
from MapImages import MAP_IMAGES
import os
from GameChat import getGameChat, updateChatEmbed, updateMessages
from StatList import BasicStatList, AdvancedStatList
from itertools import combinations
from playThread import updatePlayEmbed, checkTime, time_slots, updateOnlineThreadEmbed
# import elo as ELO
from time import strftime, localtime, gmtime
import time
import copy
from predictGame import predictGame, predictAll
import pickle
from alts import getAlts
from clans import getClanEmbed
import json
from discord.utils import get

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
    if not ONLINE_CHANNEL:
        ONLINE_CHANNEL = os.environ['ONLINE_CHANNEL']
        ONLINE_CHANNEL = int(ONLINE_CHANNEL)
except:
    print('failed to load bot token credentials')
    exit(1)

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = "!", intents = intents)

onlineCalls, gameCalls, basicStatCalls, advancedStatCalls = 0, 0, 0, 0


player_stats = Database("UYA","Player_Stats")
players_online = Database("UYA","Players_Online")
game_history = Database("UYA", "Game_History")
games_active = Database("UYA","Games_Active")
api_analytics = Database("UYA","API_Analytics")
clans = Database("UYA", "Clans")
discord_ids = Database("UYA", "Discord_IDs")
smoke_schedule = Database("UYA","Smoke_Schedule")


@client.event
async def on_ready():
    print("Bot is ready...")
    daemon.start()


    play_thread = client.get_channel(TODAYS_PLAYERS)
    await play_thread.purge(limit = 5)
    global daily_reset, updatingPlayChannel, todays_date
    # updatingPlayChannel = chat_channel
    daily_reset = False
    todays_date = strftime("%a, %b %d", localtime())
    updatingPlayChannel = await play_thread.send(embed = updatePlayEmbed(todays_date, smoke_schedule))
    play_channel.start()

    chat_channel = client.get_channel(CHAT_CHANNEL)
    global message_stack
    global message_history
    message_stack = []
    message_history = {}
    chat.start(chat_channel)

    global model
    model = pickle.load(open('uya_game_prediction(all modes).sav', 'rb'))

    global updatingOnlineMessage
    onlineThread = client.get_channel(ONLINE_CHANNEL)
    await onlineThread.purge(limit = 5)
    updatingOnlineMessage = await onlineThread.send(embed = updateOnlineThreadEmbed(players_online, player_stats, games_active, clans))
    updateOnlineThread.start()

    await checkRoles.start()





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
        if player['clan_tag'] != '':
            field+='({})\t {} [{}]\n'.format(player['status'], player['username'], player['clan_tag'])
        else:
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
            lobby += player_stats.getUsername(id) + ",\t"

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
async def teams(ctx, idx):
    global model

    games = games_active.getActiveGames()
    idx = int(idx)
    if idx >= len(games):
        #error
        await ctx.send("```Invalid Game ID```")
    else:
        game = games[idx]
        if len(game['details']['players']) % 2 != 0:
            await ctx.send("```This model is not built for uneven teams```")
        else:
            teams, probs = predictGame(game, model, player_stats)
            red, red_p = teams[0], probs[0]
            blue, blue_p = tuple(teams[1]), probs[1]


            embed = discord.Embed(
                title = "Balanced Teams",
                color=11043122
            )

            res = "Team: {}: Win Confidence {:.2f}\nTeam: {}: Win Confidence {:.2f}".format(red, red_p, blue, blue_p)
            embed.description = res
            await ctx.send(embed =embed)


@client.command()
async def teamsAll(ctx, idx):
    global model

    games = games_active.getActiveGames()
    idx = int(idx)
    if idx >= len(games):
        #error
        await ctx.send("```Invalid Game ID```")
    else:
        game = games[idx]
        if len(game['details']['players']) % 2 != 0:
            await ctx.send("```This model is not built for uneven teams```")
        else:
            teams, probs = predictAll(game, model, player_stats)
            embed = discord.Embed(
                title = "Balanced Teams",
                color=11043122
            )


            for team, prob in zip(teams, probs):
                embed.add_field(name="{}".format(team), value="Win = {:.1f}%".format(prob*100))
            await ctx.send(embed =embed)
    
    


@client.command()
async def basicStats(ctx, username):
    global basicStatCalls
    basicStatCalls+=1
    embed = discord.Embed(
        title = f"{username} Basic Stats",
        # url = "https://socomcommunity.com/servers/10684", 
        # description = "Players Online",
        color=11043122
    )
    if player_stats.exists(username):
        realName = player_stats.getRealName(username)
        info, clan = player_stats.getPlayerBasicStats(username)
        res = ""
        for stat in BasicStatList:
            field = "{}: {}\n".format(stat, info[BasicStatList[stat]])
            res+=field
        embed.add_field(name='Clan', value = clan, inline = False)
        embed.add_field(name = 'Stats', value = res, inline=False)
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

@client.command()
async def alt(ctx, username):
    await ctx.send(embed = getAlts(username))

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

@tasks.loop(minutes=0.5)
async def chat(chat_channel):
    global message_stack
    global message_history
    message_stack = updateMessages(message_stack, message_history)
    
    if len(message_stack) > 0:
        await chat_channel.send(embed = updateChatEmbed(message_stack))
        for message in message_history:
            message_history[message]+=1
            if message_history[message] == 21:
                del message_history[message]

        for message in message_stack:
            message_history[message] = 1
        message_stack = []

@tasks.loop(minutes=60)
async def play_channel():
    global daily_reset, todays_date, updatingPlayChannel
    t = int(strftime("%H", gmtime())) #gmtime = ET + 5
    if t == 10 and not daily_reset:
        print("updating T...")
        todays_date = strftime("%a, %b %d", localtime())
        smoke_schedule.resetSmokeSchedule(todays_date)
        daily_reset = True
    elif t != 10 and daily_reset:
        daily_reset = False
    await updatingPlayChannel.edit(embed = updatePlayEmbed(todays_date, smoke_schedule))
    
@client.command()
async def play(ctx):
    arg = ctx.message.content.split(" ")
    if len(arg) > 1:
        time = arg[1].lower()
        time = time if len(time) > 2 else time + "pm"
        if not checkTime(time):
            await ctx.send("```Not a valid time.```")
        else:
            if smoke_schedule.scheduleContains(ctx.message.author.name, time):
                await ctx.send("```You're already in there, you addict.```")
            else:
                smoke_schedule.addToTime(time, ctx.message.author.name)
                await ctx.send("```Welcome to tonight's smoke.```")
    else:
        time=None
        if ctx.message.author.name in playtime_slots['Anytime']:
            await ctx.send("```You're already in there, you addict.```")
        else:
            playtime_slots['Anytime'].append(ctx.message.author.name)
            await ctx.send("```Welcome to tonight's smoke.```")

    await play_channel()

@client.command()
async def clan(ctx, clan_name):
    clan_name = clan_name.lower()
    clan = clans.collection.find_one({'clan_name_lower':clan_name})
    if not clan:
        await ctx.send("```Clan Not Found```")
    else:
        await ctx.send(embed = getClanEmbed(clan))

@tasks.loop(minutes=120)
async def checkRoles():
    caps = player_stats.getTop5('stats.ctf.ctf_caps')
    saves = player_stats.getTop5('stats.ctf.ctf_saves')
    baseDmg = player_stats.getTop5('stats.overall.overall_base_dmg')
    kills = player_stats.getTop5('stats.overall.kills')
    wins = player_stats.getTop5('stats.overall.wins')
    nodes = player_stats.getTop5('stats.overall.nodes')
    squats = player_stats.getTop5('stats.other.squats')
    suicides = player_stats.getTop5('stats.overall.suicides')

    specialRoles = {
        'Top 5 Rusher':caps,
        'Top 5 Defender':saves,
        'Top 5 Killer':kills,
        'Top 5 Winner':wins,
        'Top 5 Node Technician': nodes,
        'Top 5 Base Destroyer': baseDmg,
        'Top 5 Swimmer' :suicides,
        'Top 5 T-Bagger' : squats
    }

    users = discord_ids.getAll()
    aquatos = get(client.guilds, id = 357568581178884107)
    for username in users:
        member = get(aquatos.members, id = users[username])
        for role in specialRoles:
            if username in specialRoles[role]:
                role = get(aquatos.roles, name = role)
                await member.add_roles(role)
            else:
                role = get(aquatos.roles, name = role)
                if role in member.roles:
                    await member.remove_roles(role)
                
@client.command()
async def assign(ctx, uya_name):
    if player_stats.exists(uya_name):
        id = ctx.author.id

        if not discord_ids.exists(uya_name):
            discord_ids.addID(uya_name, id, player_stats)            
            await ctx.send(f"```{uya_name} added```")
        else:
            await ctx.send("```Name already in here```")

    else:
        await ctx.send("```Player Not Found```")

    
@tasks.loop(minutes = 0.1)
async def updateOnlineThread():
    global updatingOnlineMessage

    await updatingOnlineMessage.edit(embed = updateOnlineThreadEmbed(players_online, player_stats, games_active, clans))
    



        




#replace with token
client.run(BOT_TOKEN)