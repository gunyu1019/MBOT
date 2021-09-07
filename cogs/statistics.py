import json
import logging
from typing import Union

import discord
from discord.ext import commands

from module.message import Message
from utils.database import Database

logger = logging.getLogger(__name__)
DBS = None


class StatisticsReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def to_json(data: Union[dict, list]):
        return json.dumps(data, indent=4, ensure_ascii=True)

    @commands.Cog.listener()
    async def on_interaction_message(self, message: Message):
        database = Database(bot=self.bot, guild=message.guild)
        if not database.get_activation("statistics"):
            return

        author = message.author
        data = {
            "channel_id": message.channel.id,
            "guild_id": message.guild.id,
            "author_id": author.id,
            "author_name": author.name,
            "author_tag": author.discriminator,
            "content": message.content,
            "embeds": self.to_json([embed.to_dict() for embed in message.embeds]),
            "attachment": self.to_json([attachment.url for attachment in message.attachments]),
            "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "bot": author.bot
        }

        if len(message.stickers) > 0:
            fetch_stickers = [await sticker.fetch() for sticker in message.stickers]
            data.update({
                "stickers": self.to_json([
                    sticker.url for sticker in message.stickers
                ]),
                "stickers_type": self.to_json([
                    "Guild" if isinstance(sticker, discord.GuildSticker) else "Standard" for sticker in fetch_stickers
                ])
            })
        if message.webhook_id is not None:
            data["webhook_id"] = message.webhook_id

        database.set_data("message", data=data, key=str(message.id))
        return


def setup(client):
    client.add_cog(StatisticsReceive(client))
