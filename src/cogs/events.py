import discord
from discord.ext import commands
import helpers.vars as vars
from helpers.helpers import createLogger, createEmbed, conn, bot
from helpers.db import createTables

logger = createLogger(vars.bot_abbr)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        response = f'We have logged in as {bot.user}. Bot currently installed in {len(bot.guilds)} servers.'
        logger.info(response)
        print(response)

        # Create SQL Tables & Connect to DB
        createTables()

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == bot.user:
            return
        
        print(message.content)
        print(message.channel.id)
        print(message.channel.history)
        
        # Open DB Cursor
        cur = conn.cursor()
        cur.row_factory = lambda cursor, row: row[0]
        
        # Check if server has been configured yet. Get channel name if so. Do nothing if not.
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": message.guild.id}).fetchall()
        if len(config_check)==0:
            return
        else:
            dt_channel_id = cur.execute("SELECT dt_channel_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": message.guild.id}).fetchone()

        print(message.channel.id)
        if message.channel.id != dt_channel_id:
            return

        # Get all starred messages in Starboard Channel from DB
        dub_length = cur.execute("SELECT COUNT(*) FROM DUBS WHERE guild_id=:guild_id", {"guild_id": message.guild.id}).fetchone()
        print(dub_length)

        if dub_length == 0:
            # Get ALL Messages
            messages = await message.channel.history(limit=1000).flatten()
            print(messages)
            for i in messages:
                print(i.content)
        else:
            # Just get this message
            dub_type = None
            try:
                cur.execute("INSERT INTO DUBS VALUES (?, ?, ?, ?, ?, ?, ?)", (
                        message.id,
                        message.guild.id,
                        message.channel.id,
                        message.content,
                        message.author,
                        message.created_at,
                        dub_type
                    )
                )
                conn.commit()
                # response = f"{channel_name} has been added to this server's {vars.bot_name} channel exceptions."
                # await ctx.channel.send(response)
                # logger.info(response)
            except:
                pass

async def setup(bot):
    await bot.add_cog(Events(bot))