import nextcord
from nextcord.ext import commands
import json 
import chartGen
import matplotlib.pyplot as plt
import io
from datetime import datetime

#discord bot setup
description = '''Bot for generating charts based on discord servers. https://github.com/TCA166/chartBot'''
intents = nextcord.Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='$', description=description, intents=intents)

async def handleChannel(channel:nextcord.channel) -> list:
    result = []
    #print(channel.name)
    i = 1
    if hasattr(channel, 'history'):
        async for message in channel.history(limit=None):
            #print(i, end="\r")
            result.append((message.author.id, message.content, str(message.created_at), [(r.count, r.emoji if isinstance(r.emoji, str) else ':%s:' % r.emoji.name ) for r in message.reactions]))
            i += 1

    return result
    

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.slash_command(description='Does a complete discord server scan, and sends back the json result.')
async def initialise(interaction:nextcord.Interaction):
    await interaction.send('Starting data gathering...')
    jsonR = {}
    server = interaction.guild
    print('Fetched server with name:%s' % server.name)
    jsonR['name'] = server.name
    jsonR['desc'] = server.description
    jsonR['mbmr'] = []
    for member in server.members:
        memb = {}
        memb['name'] = member.name
        memb['id'] = member.id
        memb['join'] = str(member.joined_at)
        memb['nick'] = member.nick
        jsonR['mbmr'].append(memb)
    jsonR['ownr'] = server.owner_id
    if server.icon is not None:
        jsonR['icon'] = server.icon.url
    jsonR['emjs'] = [(e.name, e.url) for e in server.emojis]
    jsonR['chnl'] = {}
    for channel in server.channels:
        if not hasattr(channel, 'text_channels'): 
            jsonR['chnl'][channel.name] = await handleChannel(channel)

    with open('%s.json' % server.id, 'w+') as f:
        f.write(json.dumps(jsonR))
    await interaction.send(file=nextcord.File('%s.json' % server.id))
    print('Done')

@bot.slash_command(description='Creates a 3d message count graph. X=Time, Y=count, Z=channels.')
async def message_count_chart(interaction:nextcord.Interaction, usr:nextcord.Member=None, ignore_channel:str='', contains:str=''):
    if usr is not None:
        usr = usr.id
    ignore_channel = ignore_channel.split(',')
    server = interaction.guild
    try:
        with open('%s.json' % server.name, 'r+') as f:
            j = json.loads(f.read())
    except:
        interaction.send("Server hasn't been initialised. Cannot perform command.")
        return
    ax = chartGen.generateMsgCountChart(j, usr, ignore_channel, contains)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    file = nextcord.File(fp=buf, filename='plot.png')
    await interaction.send(file=file)

@bot.slash_command(description='Creates a pie chart of member activity.')
async def active_usr_chart(interaction:nextcord.Interaction, ignore_channel:str='', max_date:str=None, min_date:str=None, contains:str=''):
    if len(ignore_channel) == 0:
        ignore_channel = ()
    else:
        ignore_channel = ignore_channel.split(',')
    
    if max_date is not None:
        max_date = datetime.strptime(max_date[0:10], "%Y-%m-%d")
    if min_date is not None:
        min_date = datetime.strptime(min_date[0:10], "%Y-%m-%d")
    server = interaction.guild
    try:
        with open('%s.json' % server.name, 'r+') as f:
            j = json.loads(f.read())
    except:
        interaction.send("Server hasn't been initialised. Cannot perform command.")
        return
    ax = chartGen.generateActiveUsrChart(j, ignore_channel, max_date, min_date, contains)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    file = nextcord.File(fp=buf, filename='plot.png')
    await interaction.send(file=file)

@bot.slash_command(description='Creates a bar chart of word occurences through time.')
async def word_chart(interaction:nextcord.Interaction, ignore_channel:str='', ignore_urls:bool=True, cutoff:int=20, min_len:int=3, contains:str=''):
    if len(ignore_channel) == 0:
        ignore_channel = ()
    else:
        ignore_channel = ignore_channel.split(',')
    server = interaction.guild
    try:
        with open('%s.json' % server.name, 'r+') as f:
            j = json.loads(f.read())
    except:
        interaction.send("Server hasn't been initialised. Cannot perform command.")
        return
    ax = chartGen.generateWordChart(j, ignore_channel, True, ignore_urls, cutoff, min_len, contains)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    file = nextcord.File(fp=buf, filename='plot.png')
    await interaction.send(file=file)

@bot.slash_command(description='Creates a bar chart of reactions through time.')
async def reaction_chart(interaction:nextcord.Interaction, ignore_channel:str='', cutoff:int=100):
    if len(ignore_channel) == 0:
        ignore_channel = ()
    else:
        ignore_channel = ignore_channel.split(',')
    server = interaction.guild
    try:
        with open('%s.json' % server.name, 'r+') as f:
            j = json.loads(f.read())
    except:
        interaction.send("Server hasn't been initialised. Cannot perform command.")
        return
    ax = chartGen.generateReactionChart(j, ignore_channel, cutoff)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    file = nextcord.File(fp=buf, filename='plot.png')
    await interaction.send(file=file)

with open("auth.json") as f:
    bot.run(json.loads(f.read())["key"])

    