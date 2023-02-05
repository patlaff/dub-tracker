import discord
from discord.ext import commands
import helpers.vars as vars
from helpers.helpers import createLogger, checkServerConfig, conn

logger = createLogger('config')

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### SET ###
    @commands.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    @commands.command(
        help=f"Use this command to set the {vars.bot_name} channel for this server. Ex: |set <channel> Ex: |set {vars.bot_name}-channel",
	    brief=f"Use {vars.command_prefix}set <channel_name> to set the {vars.bot_name} channel for this server."
    )
    async def set(self, ctx, dt_channel_name):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        guild = self.bot.get_guild(guild_id)

        # Check if Channel exists in Server
        channel = discord.utils.get(guild.channels, name=dt_channel_name)
        if not channel:
            response = f"Channel, {dt_channel_name}, does not exist on this server."
            await ctx.channel.send(f"{response} Please try this command again with a valid channel.")
            logger.info(response)
            return
        else: 
            dt_channel_id = channel.id

        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            # Insert initial config with default reaction_count_threshold if no config present in DB
            cur.execute(f"INSERT INTO CONFIGS VALUES (?, ?)", (
                guild_id,
                dt_channel_id
                )
            )
            conn.commit()
            response = f"Channel, {dt_channel_name}, has been added as this server's {vars.bot_name}. Default reaction threshold was set to {vars.default_reaction_count_threshold}. Use |threshold to set a custom threshold."
            await ctx.channel.send(response)
            logger.info(response)
        else:
            # Update existing config with new starboard if config present in DB
            cur.execute(f"""
                UPDATE CONFIGS
                SET dt_channel_id=:dt_channel_id
                WHERE guild_id=:guild_id
            """, {"guild_id": guild_id, "dt_channel_id": dt_channel_id})
            conn.commit()
            response = f"Channel, {dt_channel_name}, has been updated as this server's {vars.bot_name}."
            await ctx.channel.send(response)
            logger.info(response)

        cur.close()

async def setup(bot):
    await bot.add_cog(Config(bot))