import nextcord
from nextcord.ext import commands
import datetime
import json 

#discord bot setup
description = ''' '''
intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='//', description=description, intents=intents)

serverID = 691679955871989841

async def handleChannel(channel:nextcord.channel) -> list:
    result = []
    print(channel.name)
    i = 1
    try:
        async for message in channel.history(limit=None):
            print(i, end="\r")
            result.append((message.author.id, message.content, str(message.created_at), [(r.count, str(r.emoji)) for r in message.reactions]))
            i += 1
    except:
        print("Can't access channel")
    return result
    

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Attempting to fetch the server with id %d' %serverID)
    jsonR = {}
    server = bot.get_guild(serverID)
    if server == None:
        print('Failed to get the server')
        return
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
    jsonR['icon'] = server.icon.url
    jsonR['emjs'] = [(e.name, e.url) for e in server.emojis]
    jsonR['chnl'] = {}
    for channel in server.channels:
        if not hasattr(channel, 'text_channels'): 
            jsonR['chnl'][channel.name] = await handleChannel(channel)
            
    with open('%s.json' % server.name, 'w+') as f:
        print(jsonR)
        f.write(json.dumps(jsonR))
    print('Done')
  
with open("auth.json") as f:
    bot.run(json.loads(f.read())["key"])

    