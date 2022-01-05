import discord


def updatePlayEmbed(time, smoke_schedule):
    chat_embed = discord.Embed(
        title = 'Players Who Want To Play (ET Times)',
        color=11043122
    )

    playtime_slots = smoke_schedule.collection.find_one({'name':"Smoke Schedule"})['schedule']
    for playtime in playtime_slots:
        if len(playtime_slots[playtime]) > 0:
            field = ''
            for player in playtime_slots[playtime]:
                field+="{}\n".format(player)
            chat_embed.add_field(name ="Time: {} | {} Players".format(playtime, len(playtime_slots[playtime])), value = field, inline='False')
        

    chat_embed.add_field(name ="Smoke Date", value = time, inline='False')
    chat_embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
    return chat_embed

def checkTime(time):
    return time in time_slots

time_slots = {
    '1am':[],
    '2am':[],
    '3am':[],
    '4am':[],
    '5am':[],
    '6am':[],
    '7am':[],
    '8am':[],
    '9am':[],
    '10am':[],
    '11am':[],
    '12pm':[],
    '1pm':[],
    '2pm':[],
    '3pm':[],
    '4pm':[],
    '5pm':[],
    '6pm':[],
    '7pm':[],
    '8pm':[],
    '9pm':[],
    '10pm':[],
    '11pm':[],
    '12am':[],
    "Anytime":[]    
}

def updateOnlineThreadEmbed(players_online, player_stats, games_active,clans):
    embed = discord.Embed(
        title = "Aquatos",
        # url = "https://socomcommunity.com/servers/10684", 
        # description = "Players Online",
        color=11043122
    )
    #Online Players
    players = players_online.getOnlinePlayers()
    field = '```None' if len(players) == 0 else '```'
    for player in players:
        if player['clan_id'] != -1:
            field+=f"{player['username']}    [{player['clan_tag']}]\n"
        else:
            field+=f"{player['username']}\n"

    embed.add_field(name = f'Players Online [{len(players)}]', value = field+"```", inline = False)
    #Games
    games = games_active.getActiveGames()
    field = '```None```' if len(games) == 0 else ''
    for game in games:
        host = game['details']['host']
        status = game['details']['status'].replace("_", " ")
        arena = game['details']['map'].replace("_", " ")
        mode = game['details']['gamemode']
        weapons = ""
        for gun in game['details']['weapons']:
            weapons+=gun+", "
        
        weapons = "Wrench Only" if weapons == "" else weapons[:len(weapons)-2]

        lobby = ""
        for name in game['details']['players']:
            lobby += name + ", "

        value = """```
Host: {}
Status: {}
Map: {}
Gamemode: {}
Weapons: {}
Players: {}```\n""".format(host, status, arena, mode, weapons, lobby)
        field+=value
    embed.add_field(name = f"Active Games [{len(games)}]", value = field, inline = False)

    #clans
    clanList, numsClans = clans.getOnlineClans(players)
    if numsClans == 0: clanList = "```None```"
    embed.add_field(name=f'Clans Online [{numsClans}]', value = clanList)

    return embed