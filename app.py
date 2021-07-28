import asyncio
import logging
import argparse
import discord

from discord import abc, utils
from discord.ext import tasks

logger = logging.getLogger('discord')
# handler = logging.FileHandler(filename='app.log', encoding='utf-8', mode='w')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token", help="token to bot auth")
parser.add_argument("-c", "--channel", help="ID for RO channel on server")
parser.add_argument("-e", "--exclude", help="roles to exclude for serve")

args = parser.parse_args()

token = args.token if args.token else input('Token: ')
channel_id = args.channel if args.channel else input('RO channel ID: ')
exclude = args.exclude if args.exclude else input('Exclude: ')

excludes = [x for x in exclude.split(',')]

client = discord.Client()

cache = {}

@tasks.loop(seconds=1800)
async def maintain_presence():
    logger.debug("confirm we are still here")
    await client.change_presence(status=discord.Status.online, activity=None)


@client.event
async def on_ready():
    logger.info("Logged in as {}".format(client.user.name))
    logger.debug("gathering info about allowed channel")
    allowed_channel = client.get_channel(int(channel_id))
    logger.debug("{} channel found".format(allowed_channel.name))
    logger.debug("gathering pinned messages in allowed channel")
    pinned_messages = await abc.Messageable.pins(allowed_channel)
    logger.debug("{} pinned messages found".format(len(pinned_messages)))
    logger.debug("gathering info about allowed message")
    first_pinned_message_id = int(pinned_messages[0].id)
    allowed_message = await abc.Messageable.fetch_message(allowed_channel, first_pinned_message_id)
    logger.debug("allowed channel and message found")
    cache["channel"] = allowed_channel
    cache["message"] = allowed_message
    logger.info("bot is ready")


@client.event
async def on_raw_reaction_add(payload):
    if validate_payload(payload):
        guild = client.get_guild(payload.guild_id)
        user = await guild.fetch_member(payload.user_id)
        role_name = payload.emoji.name

        guild_roles = [i.name for i in guild.roles]
        user_roles = [i.name for i in user.roles]

        for role in excludes:
            if role in guild_roles:
                guild_roles.remove(role)

        role = utils.get(guild.roles, name=role_name)

        if (role_name in guild_roles) and (role_name not in user_roles):
            await user.add_roles(role)
            logger.info("{} have subscribed on {}".format(user.name, role))


@client.event
async def on_raw_reaction_remove(payload):
    if validate_payload(payload):
        guild = client.get_guild(payload.guild_id)
        user = await guild.fetch_member(payload.user_id)
        role_name = payload.emoji.name

        guild_roles = [i.name for i in guild.roles]

        for role in excludes:
            if role in guild_roles:
                guild_roles.remove(role)

        role = utils.get(guild.roles, name=role_name)

        if (role_name in guild_roles) and (role_name not in excludes):
            await user.remove_roles(role)
            logger.info("{} have unsubscribed from {}".format(user.name, role))


def validate_payload(payload):
    if cache['channel'].id == payload.channel_id:
        if cache['message'].id == payload.message_id:
            logger.debug("payload validation success")
            return True
    else:
        logger.debug("payload validation failed")
        return False


client.run(token)
