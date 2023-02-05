import os
import sys
import logging
import discord
from discord.ext import commands
import helpers.vars as vars
import sqlite3 as sql

def createDir(path):
    # Check whether the specified path exists or not
    path_exist = os.path.exists(path)
    # Create path if not exists
    if not path_exist:
        os.makedirs(path)
        print(f"Required path {path} not detected, so we created it!")
    return path

def createChildDir(folder):
    ## Create log folder if not exists ##
    path = os.path.join(sys.path[0], folder)
    # Check whether the specified path exists or not
    path_exist = os.path.exists(path)
    # Create log path if not exists
    if not path_exist:
        os.makedirs(path)
        print(f"Required path {path} not detected, so we created it!")
    return path

def createLogger(logger_name, folder_name=f'./{vars.bot_abbr}/logs'):
    # Configure logger
    if folder_name[:1] == '/':
        log_path = createDir(folder_name)
    else:
        log_path = createChildDir(folder_name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(os.path.join(log_path, f'{logger_name}.log'))
    handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def createDbConn(db_name=vars.bot_abbr, folder_name=f'./{vars.bot_abbr}/db'):
    # folder_name should map to volume mount location in docker run command
    if folder_name[:1] == '/':
        db_path = createDir(folder_name)
    else:
        db_path = createChildDir(folder_name)
    createDir(folder_name)
    conn = sql.connect(os.path.join(db_path, f'{db_name}.db'))
    return conn

conn = createDbConn()

def createBot():
    # Create and configure Discord bot
    intents = discord.Intents.default()
    intents.message_content = True
    help_command = commands.DefaultHelpCommand(
        no_category = 'General'
    )
    bot = commands.Bot(
        command_prefix=vars.command_prefix,
        intents=intents,
        help_command=help_command
    )
    return bot

bot = createBot()

def insertKeywordMessage(message):
    cur = conn.cursor()
    dub_type = None
    content = message.content.lower()
    if vars.keyword.lower() in content:
        for bin in vars.bins:
            if bin.lower() in content:
                dub_type = bin
                break
        try:
            cur.execute("INSERT INTO DUBS VALUES (?, ?, ?, ?, ?, ?, ?)", (
                    message.id,
                    message.guild.id,
                    message.channel.id,
                    message.content,
                    message.author.name,
                    message.created_at,
                    dub_type
                )
            )
            conn.commit()
            print(f"{message.id} inserted into table, DUBS, with dub_type, {dub_type}")
        except Exception as e:
            print(e)
    cur.close()

def createEmbed(ctx, total_dubs, binned_dubs, user):
    # Craft vars
    solo_dubs = binned_dubs[vars.bins.index('solo')]
    duo_dubs = binned_dubs[vars.bins.index('duo')]
    trio_dubs = binned_dubs[vars.bins.index('trio')]
    squad_dubs = binned_dubs[vars.bins.index('quad')]
    # Create Embed Content
    embedVar = discord.Embed(description=f"Dub Count on server: {ctx.guild.name}", color=0xffffff)
    embedVar.set_author(name=user) #, icon_url=message.author.display_avatar)
    embedVar.insert_field_at(index=1, name="TOTAL", value=total_dubs[0])
    embedVar.insert_field_at(index=2, name='', value='\u200b')
    embedVar.insert_field_at(index=3, name="👨", value=solo_dubs[0]) #, inline=True)
    embedVar.insert_field_at(index=4, name="👨‍👦", value=duo_dubs[0], inline=True)
    embedVar.insert_field_at(index=5, name="👨‍👨‍👦", value=trio_dubs[0], inline=True)
    embedVar.insert_field_at(index=6, name="👨‍👨‍👦‍👦", value=squad_dubs[0])
    return embedVar

async def checkServerConfig(ctx, logger, guild_id):
    cur = conn.cursor()
    config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
    if len(config_check)==0:
        response = f"Please configure a {vars.bot_name} channel for this server before setting additional configurations. Use |set to do so."
        logger.info(response)
        await ctx.channel.send(response)
        return None
    else:
        return 1