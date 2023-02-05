import discord
from discord.ext import commands
import helpers.vars as vars
from helpers.helpers import createLogger, insertKeywordMessage, createEmbed, conn, bot
from helpers.db import createTables
import sqlite3 as sql

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
        
        if message.content.startswith(vars.command_prefix):
            return


        # Open DB Cursor
        cur = conn.cursor()
        cur.row_factory = lambda cursor, row: row[0]

        # Check if server has been configured yet. Get channel name if so. Do nothing if not.
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": message.guild.id}).fetchall()
        if len(config_check)==0:
            return
        else:
            dt_channel_id = cur.execute("SELECT dt_channel_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": message.guild.id}).fetchone()

        if message.channel.id != dt_channel_id:
            return

        # Get all starred messages in Starboard Channel from DB
        dub_length = cur.execute("SELECT COUNT(*) FROM DUBS WHERE guild_id=:guild_id", {"guild_id": message.guild.id}).fetchone()
        print(f"dub_length: {dub_length}")

        if dub_length == 0:
            # Get ALL Messages
            async for m in message.channel.history(limit=1000):
                insertKeywordMessage(m)
        else:
            # Just log this one message
            insertKeywordMessage(message)
            # response = f"{channel_name} has been added to this server's {vars.bot_name} channel exceptions."
            # await ctx.channel.send(response)
            # logger.info(response)
    

    ### GET DUB BOARD ###
    # @commands.has_permissions(
    #     manage_channels=True,
    #     manage_messages=True
    # )
    @commands.command(
        help=f"Use this command to view the {vars.bot_name} leaderboard for this server. Ex: {vars.command_prefix}board [user] Ex: {vars.command_prefix}board A_Triscuit",
	    brief=f"Use {vars.command_prefix}board [user] to view the {vars.bot_name} leaderboard for this server."
    )
    async def board(self, ctx, user=None):
        cur = conn.cursor()

        binned_dubs = []
        if user:
            total_dubs = cur.execute("SELECT COUNT(*) FROM DUBS WHERE guild_id=:guild_id AND author=:user", {"guild_id": ctx.guild.id, "user": user}).fetchone()
            for bin in vars.bins:
                dub_bin = cur.execute("SELECT COUNT(*) FROM DUBS WHERE guild_id=:guild_id AND author=:user AND dub_type=:dub_type", {"guild_id": ctx.guild.id, "user": user, "dub_type": bin}).fetchone()
                binned_dubs.append(dub_bin)
            embedVar = createEmbed(ctx, total_dubs, binned_dubs, user)
        else:
            try:
                total_dubs = cur.execute("SELECT COUNT(*) FROM DUBS WHERE guild_id=:guild_id", {"guild_id": ctx.guild.id}).fetchone()
            except Exception as e:
                print(e)
            for bin in vars.bins:
                try:
                    dub_bin = cur.execute("SELECT COUNT(*) FROM DUBS WHERE guild_id=:guild_id AND dub_type=:dub_type", {"guild_id": ctx.guild.id, "dub_type": bin}).fetchone()
                except Exception as e:
                    print(e)
                binned_dubs.append(dub_bin)
            embedVar = createEmbed(ctx, total_dubs, binned_dubs, "All")

        await ctx.channel.send(embed=embedVar)
        cur.close()

async def setup(bot):
    await bot.add_cog(Events(bot))