import json
import logging
import os

import discord
from discord.ext import commands
from typing import Union, List

from config.config import parser
from module.interaction import ComponentsContext, InteractionContext
from module.message import Message, MessageSendable
from utils.convert import Convert
from utils.database import Database
from utils.directory import directory
from utils.models import Ticket

logger = logging.getLogger(__name__)
DBS = None


class StatisticsReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction_message(self, message: Message):
        database = Database(bot=self.bot, guild=message.guild)
        if not database.get_activation("statistics"):
            return
        database.set_data("message", datas={
            "channel_id": message.channel.id,
            "guild_id": message.guild.id,
            "author_id": message.author.id,
            "author_name": message.author.name,
            "author_tag": message.author.discriminator,
            "content": message.content,
            "embeds": json.dumps(
                [embed.to_dict() for embed in message.embeds],
                indent=4, ensure_ascii=True
            ),
            "attachment": json.dumps(
                [attachment.url for attachment in message.attachments],
                indent=4, ensure_ascii=True
            ),
            "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "bot": message.author.bot
        }, key=str(message.id))
        return


def setup(client):
    client.add_cog(StatisticsReceive(client))
