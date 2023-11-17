# Discord Gamebot (Experiment)

*Summary: Very experimental bot for testing out fun chat experiences with Glif, and building out our bot scaffolding.*

Currently supports creating image, video, and short 4-scene "films". 

Internal version of the bot lives at [Stan's Test Server](https://discord.gg/mFa2Wtwb).

Linear issues: 
- https://linear.app/glif/issue/GLIF-484/glapp-discord-scaffolding-v1
- https://linear.app/glif/issue/GLIF-482/games-bots-and-nextglif-prototypes

Built using the Python [interactions](https://github.com/interactions-py/interactions.py) discord bot library. 

## Setup

Needed environment variables: (May also be in .env file)

- DISCORD_TOKEN : unique token for your bot.
- ACTIVE_CHANNEL_ID : id of your discord server. 
- REPLICATE_API_TOKEN : api token for [Replicate](https://replicate.com/) music API. 

Make sure there is a folder called `temp_files`. Over time this may fill up and need to be cleaned. 

## Running

### On Replit

Load the repo into Replit, set up the env vars (aka secrets) and you're good to go!

### Local

*TODO: Needs testing and fleshing out.*

- Clone the repository.
- Install the required dependencies using `poetry install`. 
- Create a new Discord bot on the Discord Developer Portal.
- Copy the bot token and paste it into a `.env` file.
- Copy the server ID and paste it into a `.env` file.
- Run the bot using `python main.py`.
- In Discord, go to the chosen channel and type `/` to see list of commands.


