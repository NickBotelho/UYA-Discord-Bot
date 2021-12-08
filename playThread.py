import discord
from time import strftime, localtime
import time
import os
os.environ['TZ'] = 'EST+05EDT,M4.1.0,M10.5.0'
time.tzset()
def updatePlayEmbed(stack):
    chat_embed = discord.Embed(
        title = 'Players Who Want To Play',
        color=11043122
    )
    field = ""
    for user in stack:

        field+= "{}\n".format(user)
    field = "None" if len(field) == 0 else field
    chat_embed.add_field(name ="Total = {}".format(len(stack)), value = field, inline='False')
    chat_embed.add_field(name ="Smoke Date", value = strftime("%a, %b %d", localtime()), inline='False')
    chat_embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
    return chat_embed