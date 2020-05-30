import discord
import asyncio
import logging

from discord.ext import commands
from discord.utils import get

logger = logging.getLogger('discord')
# handler = logging.FileHandler(filename='app.log', encoding='utf-8', mode='w')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

token = ''
channel_id = ''
excludes = ['foo', 'bar']

client = discord.Client()

@client.event
async def on_ready():
    logger.info("Logged in as {}".format(client.user.name))
    logger.info("gathering pinned messages")
    channel = client.get_channel(channel_id)
    emojis = channel.server.emojis
    msg = await client.pins_from(channel)
    logger.info("{} pinned messages found".format(len(msg)))
    message = await client.get_message(channel, msg[0].id)
    client.messages.append(message)
    logger.info("bot is ready")

@client.event
async def on_reaction_add(reaction, user):
    if reaction.custom_emoji:
        server_roles = [i.name for i in user.server.roles]
        user_roles = [i.name for i in user.roles]
        for role in excludes:
            if role in server_roles:
                server_roles.remove(role)
        role = reaction.emoji.name
        if (role in server_roles) and (role not in user_roles):
            role = get(user.server.roles, name=reaction.emoji.name)
            await client.add_roles(user, role)
            logger.info("{} have subscribed on {}".format(user.name, role))

@client.event
async def on_reaction_remove(reaction, user):
    if reaction.custom_emoji:
        user_roles = [i.name for i in user.roles]
        role = reaction.emoji.name
        if (role in user_roles) and (role not in excludes):
            role = get(user.server.roles, name=reaction.emoji.name)
            await client.remove_roles(user, role)
            logger.info("{} have unsubscribed from {}".format(user.name, role))

client.run(token)