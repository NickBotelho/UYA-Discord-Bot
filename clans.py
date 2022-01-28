import discord
import collections

def getClanEmbed(clan, player_stats):
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
    embed.add_field(name='Clan War Stats', value = field, inline=False)

    field = ""
    powerStats = collections.Counter()

    members = clan['member_names']
    for member in members:
        field+= f"-{member}\n"
        player = player_stats.collection.find_one({'username_lowercase': member.lower()})
        basicStats = player['stats']['overall']
        elo = player['advanced_stats']['elo']
        powerStats.update(basicStats)
        powerStats.update(elo)


    embed.add_field(name='Members', value=field, inline = False)

    field = ''
    field += "Wins: {}\n".format(powerStats['wins'])
    field += "Losses: {}\n".format(powerStats['losses'])
    field += "Kills: {}\n".format(powerStats['kills'])
    field += "Deaths: {}\n".format(powerStats['deaths'])
    field += "Suicides: {}\n".format(powerStats['suicides'])
    field += "Base Damage: {}\n".format(powerStats['overall_base_dmg'])
    field += "Nodes: {}\n".format(powerStats['nodes'])
    field += "Average Elo: {}\n".format(powerStats['overall']//len(members))


    embed.add_field(name='Power Stats', value=field, inline = False)

    return embed

