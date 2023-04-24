# chartBot

A nextcord powered discord bot for generating cool charts from your discord server.

## How it works

In order to properly generate charts the bot first needs to perform a full server scan.
This is done using the slash command initialize.
Once the scan is performed and the bot announces that you can perform additional commands to generate the charts themselves.
Additionally the scan result is sent as a json file to the channel the command was issued in, allowing the users themselves to perform all kinds of analysis.

## Capabilities

So far this bot is able to generate 4 kinds of charts:

1. 3d line chart of the number of messages sent in each channel
2. Pie chart of the share each user had in total number of messages sent
3. Stacked bar chart of all reactions showing the total number of reactions, and the part each reaction played in that total.
4. Bar chart of most used words.

## Privacy

The scan result is stored locally(to ensure other commands can be issued fluidly) and sent to the channel itself.
It contains all messages ever sent within the server along with data on server members and server emojis.
Anything not available to the bot client on the server is not going to be included in the scan result, and the scan itself is not that different from what an ordinary user can accomplish by just going through message history.

## Setup

Ensure there is an auth.json file located next to the bot.py file, and that the auth.json file contains the auth secret under the "key" key.

## License

[![CCimg](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)  
This work is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).  
