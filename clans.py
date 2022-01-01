import discord
def getClanEmbed(clan):
    embed = discord.Embed(
    title = f"{clan['clan_name']}",
    description = f"[ {clan['clan_tag']} ]",
    color=11043122
    )

    embed.add_field(name = 'Leader', value=clan['leader_account_name'], inline=False)
    stats = clan['stats']
    field = ""
    for stat in stats:
        field+=f"{stat}: {stats[stat]}\n"
    embed.add_field(name='Stats', value = field, inline=False)

    field = ""
    members = clan['member_names']
    for member in members:
        field+= f"-{member}\n"
    
    embed.add_field(name='Members', value=field, inline = False)
    return embed

