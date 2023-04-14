import matplotlib.pyplot as plt
from matplotlib import dates
import json
import numpy as np
from datetime import datetime, timedelta

def generateMsgCountChart(data:dict) -> None:
    ax = plt.figure().add_subplot(projection='3d')

    timeMaxs = []
    timeMins = []

    j['chnl'] = dict(sorted(j['chnl'].items(), key=lambda k: len([k])))

    i = 1
    for key, channel in j['chnl'].items():
        if len(channel) > 2:
            time = [datetime.strptime(t[2][0:10], "%Y-%m-%d") for t in channel]
            #print(time)
            delta = max(time) - min(time)
            timeMaxs.append(max(time))
            timeMins.append(min(time))
            times = [str(min(time) + timedelta(days=i))[0:10] for i in range(delta.days + 1)]
            values = {}
            for msg in channel:
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
            print(times)
            print(ys)
            ax.plot(dates.datestr2num(times), ys, zs=i * 30, zdir='z', label=key)
            i += 1

    ax.set_xlabel('Czas', linespacing=3)
    ax.set_ylabel('Ilość wiadomości')
    ax.set_title('Ilość wiadomości na każdym kanale w czasie', pad=20)
    ax.legend(bbox_to_anchor=(1.05, 1))
    #initialise wview
    ax.view_init(elev=120., azim=-50, roll=45)
    #hide the z axis
    ax.zaxis.line.set_lw(0.)
    ax.set_zticks([])
    years_fmt = dates.DateFormatter('%Y-%m')
    ax.xaxis.set_major_formatter(years_fmt)
    plt.show()


if __name__ == "__main__":
    filename = input("Input json filename:")
    with open(filename, 'r') as f:
        data = f.read()
    j = json.loads(data)
    generateMsgCountChart(j)
    