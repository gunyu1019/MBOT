import json
import logging
from typing import Union

import asyncio
import discord
from discord.ext import commands

from module.message import Message, MessageDelete
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

        database.set_message(data=data, message_id=message.id, channel_id=message.channel.id)
        return

    @commands.Cog.listener()
    async def on_interaction_message_update(self, message: Message):
        database = Database(bot=self.bot, guild=message.guild)
        if not database.get_activation("statistics"):
            self.bot.dispatch("logging_message_update", before=None, after=message)
            return

        cached_message = database.get_message(message_id=message.id, channel_id=message.channel.id)
        self.bot.dispatch("logging_message_update", before=cached_message, after=message)

        data = {}

        if message.edited_at is not None:
            data["edited_timestamp"] = message.edited_at.strftime("%Y-%m-%d %H:%M:%S")

        if message.content is not None:
            data['content'] = message.content
        if message.content is not None:
            data['content'] = message.content
        if message.embeds is not None:
            data['embeds'] = self.to_json([embed.to_dict() for embed in message.embeds])
        if message.attachments is not None:
            data['attachment'] = self.to_json([attachment.url for attachment in message.attachments])
        if message.pinned is not None:
            data['pin'] = message.pinned

        if message.stickers is not None:
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
        database.set_message(data=data, message_id=message.id, channel_id=message.channel.id)
        return

    @commands.Cog.listener()
    async def on_interaction_message_delete(self, message: MessageDelete):
        database = Database(bot=self.bot, guild=message.guild)
        if not database.get_activation("statistics"):
            self.bot.dispatch("logging_message_delete", message=None, raw=message)
            return

        cached_message = database.get_message(message_id=message.id, channel_id=message.channel.id)
        self.bot.dispatch("logging_message_delete", messaeg=cached_message, raw=message)
        database.delete_message(message_id=message.id, channel_id=message.channel.id)
        return


def setup(client):
    client.add_cog(StatisticsReceive(client))
