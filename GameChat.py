import requests
import discord

CHAT_API = 'http://18.237.169.148:8281/chat'
def getGameChat():
    res = requests.get(CHAT_API)
    res = res.json()
    chat = ["{}: {}".format(message['username'], message['message']) for message in res]
    return chat if len(chat) > 0 else []

def updateChatEmbed():
    game_chat = getGameChat()
    chat_embed = discord.Embed(
        title = 'Game Chat',
        color=11043122
    )
    field = ""
    for message in game_chat:
        field+= message+"\n"
    field = "None" if len(field) == 0 else field
    chat_embed.add_field(name ="Aquatos", value = field, inline='False')
    chat_embed.set_thumbnail(url='https://static.wikia.nocookie.net/logopedia/images/c/cb/Ratchet_%26_Clank_-_Up_Your_Arsenal.png/revision/latest?cb=20140112222339')
    return chat_embed