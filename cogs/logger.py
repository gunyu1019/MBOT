import copy
import logging
from typing import Optional

import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone

from config.config import parser
from module.message import MessageEdited, MessageDelete, MessageSendable
from utils.database import Database
from utils.models import DatabaseMessage

logger = logging.getLogger(__name__)
DBS = None


class LoggingReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.embed = discord.Embed(title="\U0001F5D2 {0} 로그", colour=self.color)

    @commands.Cog.listener()
    async def on_logging_message_update(self, after: MessageEdited, before: DatabaseMessage = None):
        database = Database(bot=self.bot, guild=after.guild)
        if not database.get_activation("logging"):
            return
        log_activation = database.get_data(table="logging")
        if not log_activation.MESSAGE_UPDATE or not log_activation.MESSAGE:
            return
        return

    @commands.Cog.listener()
    async def on_logging_message_delete(self, message: Optional[DatabaseMessage], raw: MessageDelete):
        database = Database(bot=self.bot, guild=raw.guild)
        if not database.get_activation("logging"):
            return
        log_activation = database.get_data(table="logging")
        if not log_activation.MESSAGE_DELETE or not log_activation.MESSAGE:
            return

        if log_activation.message_log_channel_id is not None:
            if message is not None:
                if message.author_bot:
                    return
                embed = copy.deepcopy(self.embed)
                embed.title = embed.title.format("메시지 삭제")
                image = False
                embed.add_field(
                    name="사용자", value="{0}#{1}({2})".format(
                        message.author_name, message.author_tag, message.author_id
                    ),
                    inline=False
                )
                if message.content != "" and message.content is not None:
                    embed.add_field(name="내용", value="{0}".format(message.content), inline=False)
                if len(message.attachments) > 0:
                    embed.add_field(name="파일", value=", ".join([
                        "[{1}]({0})".format(
                            attachment,
                            "사진" if attachment.endswith(".png") or
                            attachment.endswith(".jpeg") or
                            attachment.endswith(".jpg") or
                            attachment.endswith(".webp")
                            else "파일"
                        ) for attachment in message.attachments
                    ]), inline=False)
                    for attachment in message.attachments:
                        if attachment.endswith(".png") or \
                                attachment.endswith(".jpeg") or \
                                attachment.endswith(".jpg") or \
                                attachment.endswith(".webp"):
                            embed.set_image(url=attachment)
                            image = True
                            break
                if len(message.stickers) > 0:
                    embed.add_field(name="스티커", value=", ".join([
                        "[{1}]({0})".format(
                            sticker.url,
                            sticker.name if sticker.name is not None else "스티커" + "({0}}".format(sticker.id)
                            if sticker.id is not None else ""
                        ) for sticker in message.stickers
                    ]), inline=False)
                    if not image:
                        for sticker in message.stickers:
                            if sticker.url.endswith(".png") or \
                                    sticker.url.endswith(".jpeg") or \
                                    sticker.url.endswith(".jpg") or \
                                    sticker.url.endswith(".webp"):
                                embed.set_image(url=sticker.url)
                                break
                embed.add_field(name="보낸 날짜", value="`{0}`".format(message.created_at), inline=True)
                if message.edited_at is not None:
                    embed.add_field(name="수정 날짜", value="`{0}`".format(message.edited_at), inline=True)
                embed.timestamp = datetime.now(tz=timezone("UTC"))
            channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=log_activation.message_log_channel)
            await channel.send(embed=embed)
        return


def setup(client):
    client.add_cog(LoggingReceive(client))
