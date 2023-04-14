import matplotlib.pyplot as plt
from matplotlib import dates
import json
import numpy as np
from datetime import datetime, timedelta
import re

def handleMention(text:str, members:dict) -> str:
    for mbr in members:
        text = text.replace(str(mbr['id']), mbr['name']).replace('<', '').replace('>', '')
    return text

def handleEmoji(text:str) -> str:
    return re.sub('<:.*:\d{18}>', re.findall('<(.*)\d{18}>', text)[0], text)

def generateMsgCountChart(data:dict, usr:int=None, ignoreChannel:tuple=()) -> None:
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
                if usr == None or msg[0] == usr:
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
    if len(ignoreChannel) > 0:
        ax.text(-2, 1.2, 'Ignored:%s' % str(ignoreChannel))
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
    plt.show()

def generateActiveUsrChart(data:dict, ignoreChannel:tuple=(), maxDate:datetime=None, minDate:datetime=None) -> None:
    fig, ax = plt.subplots()
    counts = {}
    for key, channel in data['chnl'].items():
        if key not in ignoreChannel:
            for msg in channel:
                date = datetime.strptime(msg[2][0:10], "%Y-%m-%d")
                if (maxDate is None or date < maxDate) and (minDate is None or date > minDate):
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
    if len(ignoreChannel) > 0:
        ax.text(-2, 1.2, 'Ignored:%s' % str(ignoreChannel))
    if maxDate is not None:
        ax.text(-2, 1.1, 'Max date:%s' % str(maxDate)[0:10])
    if minDate is not None:
        ax.text(-2, 1, 'Min date:%s' % str(minDate)[0:10])
    plt.show()

def generateWordChart(data:dict, ignoreChannel:tuple=(), ignoreUTF:bool=True, ignoreUrls:bool=True, cutoff:int=20, minLen:int=3) -> None:
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
                    if not (ignoreUrls and 'http' in word) and len(word) > minLen:
                        if word not in counts.keys():
                            counts[word] = 1
                        else:
                            counts[word] += 1
    counts = dict(sorted(counts.items(), key=lambda k: counts[k[0]], reverse=True))
    newCounts = {}
    for word, count in counts.items():
        if count > cutoff:
            newCounts[word] = count
    distance = 10
    x = np.arange(len(newCounts.keys()) * distance, step=distance)
    ax.bar(x, newCounts.values(), width=0.3 * distance)
    ax.set_xticks(x, newCounts.keys())
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='center')
    ax.set_title('Word frequency', pad=20)
    y = max(newCounts.values()) + 5
    if len(ignoreChannel) > 0:
        ax.text(-2, y + 0.12 * y, 'Ignored:%s' % str(ignoreChannel))
    if minLen > 0:
        ax.text(-2, y + 0.08 * y, 'Minimum length:%d' % minLen)
    ax.text(-2, y + 0.04 * y, 'Cutoff:%d occurences' % cutoff)
    plt.show()

if __name__ == "__main__":
    filename = input("Input json filename:")
    with open(filename, 'r') as f:
        data = f.read()
    j = json.loads(data)
    #generateMsgCountChart(j)
    #generateActiveUsrChart(j)
    generateWordChart(j, ('testowanko'))