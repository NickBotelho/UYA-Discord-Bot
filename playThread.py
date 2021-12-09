import discord


def updatePlayEmbed(playtime_slots, time):
    chat_embed = discord.Embed(
        title = 'Players Who Want To Play (ET Times)',
        color=11043122
    )

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
    '12am':[],
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
    '12pm':[],
    "Anytime":[]    
}