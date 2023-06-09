import matplotlib.pyplot as plt
from matplotlib import dates
import json
import numpy as np
from datetime import datetime, timedelta
import re
import unicodedata
from emoji import EMOJI_DATA

def handleMention(text:str, members:dict) -> str:
    for mbr in members:
        text = text.replace(str(mbr['id']), mbr['name']).replace('<', '').replace('>', '')
    return text

def handleEmoji(text:str) -> str:
    return re.sub('<:.*:\d{18}>', re.findall('<(.*)\d{18}>', text)[0], text)

def generateMsgCountChart(data:dict, usr:int=None, ignoreChannel:tuple=(), contains:str='') -> plt.axes:
    ax = plt.figure().add_subplot(projection='3d')

    timeMaxs = []
    timeMins = []

    data['chnl'] = dict(sorted(data['chnl'].items(), key=lambda k: len([k[1]])))

    i = 1
    for key, channel in data['chnl'].items():
        if len(channel) > 2 and key not in ignoreChannel:
            time = [datetime.strptime(t[2][0:10], "%Y-%m-%d") for t in channel]
            #print(time)
            delta = max(time) - min(time)
            timeMaxs.append(max(time))
            timeMins.append(min(time))
            times = [str(min(time) + timedelta(days=i))[0:10] for i in range(delta.days + 1)]
            values = {}
            for msg in channel:
                if (usr == None or msg[0] == usr) and contains in msg[1]:
                    if msg[2][0:10] not in values.keys():
                        values[msg[2][0:10]] = 1
                    else:
                        values[msg[2][0:10]] += 1
            ys = []
            for t in times:
                if t in values.keys():
                    ys.append(values[t])
                else:
                    ys.append(0)
            #print(times)
            #print(ys)
            ax.plot(dates.datestr2num(times), ys, zs=i * 30, zdir='z', label=key)
            i += 1

    ax.set_xlabel('Time', linespacing=3)
    ax.set_ylabel('Amount of messages')
    if usr != None:
        ax.set_title('Messages by %s sent through time' % [u['name'] for u in data['mbmr'] if u['id'] == usr][0], pad=20)
    else:
        ax.set_title('Messages sent through time', pad=20)
    ax.legend(bbox_to_anchor=(1.05, 1))
    #initialise wview
    ax.view_init(elev=120., azim=-50, roll=45)
    #hide the z axis
    ax.zaxis.line.set_lw(0.)
    ax.set_zticks([])
    years_fmt = dates.DateFormatter('%Y-%m')
    ax.xaxis.set_major_formatter(years_fmt)
    return ax

def generateActiveUsrChart(data:dict, ignoreChannel:tuple=(), maxDate:datetime=None, minDate:datetime=None, contains:str='') -> plt.axes:
    fig, ax = plt.subplots()
    counts = {}
    for key, channel in data['chnl'].items():
        if key not in ignoreChannel:
            for msg in channel:
                date = datetime.strptime(msg[2][0:10], "%Y-%m-%d")
                if (maxDate is None or date < maxDate) and (minDate is None or date > minDate) and contains in msg[1]:
                    if msg[0] not in counts.keys():
                        counts[msg[0]] = 1
                    else:
                        counts[msg[0]] += 1
    labels = []
    for k in counts.keys():
        usr = [u['name'] for u in data['mbmr'] if u['id'] == k][0]
        labels.append(usr)
    ax.pie(counts.values(), labels=labels, autopct='%1.1f%%')
    ax.set_title('Share of messages sent by user', pad=20)
    if len(contains) > 0:
        ax.text(-2, 1.3, 'Contains:%s' % contains)
    if len(ignoreChannel) > 0:
        ax.text(-2, 1.2, 'Ignored:%s' % str(ignoreChannel))
    if maxDate is not None:
        ax.text(-2, 1.1, 'Max date:%s' % str(maxDate)[0:10])
    if minDate is not None:
        ax.text(-2, 1, 'Min date:%s' % str(minDate)[0:10])
    return ax

def generateWordChart(data:dict, ignoreChannel:tuple=(), ignoreUTF:bool=True, ignoreUrls:bool=True, cutoff:int=20, minLen:int=3, contains:str='') -> plt.axes:
    fig, ax = plt.subplots()
    counts = {}
    for key, channel in data['chnl'].items():
        if key not in ignoreChannel:
            for msg in channel:
                if ignoreUTF:
                    msg[1] = bytes(msg[1], 'utf-8').decode("utf-8")
                words = msg[1].split(' ')
                for word in words:
                    if '<:' in word:
                        word = handleEmoji(word)
                    if '@' in word:
                        word = handleMention(word, data['mbmr'])
                    if not (ignoreUrls and 'http' in word) and len(word) > minLen and contains in word:
                        if word not in counts.keys():
                            counts[word] = 1
                        else:
                            counts[word] += 1
    counts = dict(sorted(counts.items(), key=lambda k: counts[k[0]], reverse=True))
    newCounts = {}
    for word, count in counts.items():
        if count > cutoff:
            newCounts[word] = count
    x = np.arange(len(newCounts.keys()))
    ax.bar(x, newCounts.values(), width=0.3)
    ax.set_xticks(x, newCounts.keys())
    plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='center')
    ax.set_title('Word frequency', pad=20)
    y = max(newCounts.values()) + 5
    if len(contains) > 0:
        ax.text(-2, 1.16, 'Contains:%s' % contains)
    if len(ignoreChannel) > 0:
        ax.text(-2, y + 0.12 * y, 'Ignored:%s' % str(ignoreChannel))
    if minLen > 0:
        ax.text(-2, y + 0.08 * y, 'Minimum length:%d' % minLen)
    ax.text(-2, y + 0.04 * y, 'Cutoff:%d occurences' % cutoff)
    fig.tight_layout()
    return ax

def generateReactionChart(data:dict, ignoreChannel:tuple=(), cutoff:int=100) -> plt.axes:
    fig, ax = plt.subplots(figsize=(10, 6))
    timeMaxs = []
    timeMins = []

    data['chnl'] = dict(sorted(data['chnl'].items(), key=lambda k: len([k[1]])))

    counts = {}

    labels = []

    for key, channel in data['chnl'].items():
        if len(channel) > 2 and key not in ignoreChannel:
            time = [datetime.strptime(t[2][0:7], "%Y-%m") for t in channel]
            #print(time)
            timeMaxs.append(max(time))
            timeMins.append(min(time))
            for msg in channel:
                if msg[2][0:7] not in counts.keys():
                    counts[msg[2][0:7]] = {}
                for reaction in msg[3]:
                    if reaction[1] in EMOJI_DATA.keys():
                        reaction[1] = unicodedata.normalize('NFC', reaction[1])
                        newStr = ''
                        for ch in reaction[1]:
                            try:
                                newStr += ' '.join(unicodedata.name(ch).split(' ')[-2:])
                            except ValueError:
                                newStr += str(ch.encode('utf-8'))
                            newStr += " "
                        reaction[1] = newStr
                    if reaction[1] not in counts[msg[2][0:7]].keys():
                        counts[msg[2][0:7]][reaction[1]] = reaction[0]
                    else:
                        counts[msg[2][0:7]][reaction[1]] += reaction[0]
                    if reaction[1] not in labels:
                        labels.append(reaction[1])
    
    width = 0.4

    newCounts = {}
    for label in labels:
        if label not in newCounts.keys():
            newCounts[label] = []
        for key, val in counts.items():
            if label in val.keys():
                newCounts[label].append(val[label])
            else:
                newCounts[label].append(0)

    if cutoff > 0:
        filteredCounts = {}
        for key, value in newCounts.items():
            if sum(value) > cutoff or ':' in key:
                filteredCounts[key] = value
        newCounts = filteredCounts

    bottom = np.zeros(len(counts.keys()))
    for emoji, count in newCounts.items():
        ax.bar(counts.keys(), count, width, label=emoji, bottom=bottom)
        bottom += count
        
    ax.set_title("Reactions to messages through time", pad=30)
    if len(ignoreChannel) > 0:
        ax.text(0.13, 0.91, 'Ignored:%s' % str(ignoreChannel), transform=plt.gcf().transFigure)
    if cutoff > 0:
        ax.text(0.13, 0.89, 'Cutoff:%d occurences' % cutoff, transform=plt.gcf().transFigure)
    ax.legend(fontsize=str(9), bbox_to_anchor=(0.8, 1.15))
    fig.subplots_adjust(
        top=0.88,
        bottom=0.12,
        left=0.125,
        right=0.8
    )
    plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='center')  
    return ax

if __name__ == "__main__":
    filename = input("Input json filename:")
    with open(filename, 'r') as f:
        data = f.read()
    j = json.loads(data)
    #generateMsgCountChart(j, usr=464709691952463873)
    #generateActiveUsrChart(j, ignoreChannel=('ogólny', 'wszystkie-screeny', 'porno', 'testowanko', 'lista-życzeń-do-piwnicy', 'cytaty', 'wojna'), maxDate=datetime(2022, 6, 1))
    #generateWordChart(j, ('testowanko'))
    generateReactionChart(j)
    plt.show()