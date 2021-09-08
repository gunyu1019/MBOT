import copy
import logging
from typing import Optional

import discord
from discord.ext import commands
from discord.state import ConnectionState
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

    @staticmethod
    def attachment_name(file_name: str):
        if file_name.endswith(".png") or \
                file_name.endswith(".jpeg") or \
                file_name.endswith(".jpg") or \
                file_name.endswith(".webp") or \
                file_name.endswith(".bmp") or \
                file_name.endswith(".gif"):
            return "사진"
        elif file_name.endswith(".avi") or \
                file_name.endswith(".mp4") or \
                file_name.endswith(".jpg") or \
                file_name.endswith(".webm"):
            return "영상"
        elif file_name.endswith(".avi") or \
                file_name.endswith(".mp3") or \
                file_name.endswith(".midi") or \
                file_name.endswith(".webm") or \
                file_name.endswith(".wav") or \
                file_name.endswith(".mpeg"):
            return "오디오"
        return "파일"

    @commands.Cog.listener()
    async def on_logging_message_update(self, after: MessageEdited, before: Optional[DatabaseMessage] = None):
        database = Database(bot=self.bot, guild=after.guild)
        if not database.get_activation("logging"):
            return
        log_activation = database.get_data(table="logging")
        if not log_activation.MESSAGE_UPDATE or not log_activation.MESSAGE:
            return

        state: ConnectionState = getattr(self.bot, "_connection")

        if log_activation.message_log_channel_id is not None:
            cached_message: Optional[discord.Message] = getattr(state, "_get_message")(after.id)
            embed = copy.deepcopy(self.embed)
            embed.title = embed.title.format("메시지 수정")
            if before is not None:
                if after.author.bot:
                    return
                image = False
                embed.add_field(
                    name="사용자", value="{0}#{1}({2})".format(
                        before.author_name, before.author_tag, before.author_id
                    ),
                    inline=False
                )
                if after.content is not None and after.content != before.content:
                    embed.add_field(name="변경 전 내용", value="{0}".format(before.content), inline=False)
                    embed.add_field(name="변경 후 내용", value="{0}".format(after.content), inline=False)
                if after.attachments != before.attachments:
                    if len(after.attachments) > 0 and len(before.attachments) > 0:
                        embed.add_field(name="파일", value=", ".join([
                            "[{1}]({0})".format(
                                attachment,
                                self.attachment_name(attachment)
                            ) for attachment in before.attachments
                        ]) + " → " + ", ".join([
                            "[{1}]({0})".format(
                                attachment,
                                self.attachment_name(attachment)
                            ) for attachment in after.attachments
                        ]), inline=False)
                        for attachment in after.attachments:
                            if self.attachment_name(attachment) == "사진":
                                embed.set_image(url=attachment)
                                image = True
                                break
                    elif len(after.attachments) == 0 and len(before.attachments) > 0:
                        embed.add_field(name="파일", value=", ".join([
                            "[{1}]({0})".format(
                                attachment,
                                self.attachment_name(attachment)
                            ) for attachment in before.attachments
                        ]) + " (삭제됨)", inline=False)
                        for attachment in before.attachments:
                            if self.attachment_name(attachment) == "사진":
                                embed.set_image(url=attachment)
                                image = True
                                break
                    elif len(after.attachments) > 0 and len(before.attachments) == 0:
                        embed.add_field(name="파일", value=", ".join([
                            "[{1}]({0})".format(
                                attachment,
                                self.attachment_name(attachment)
                            ) for attachment in after.attachments
                        ]) + " (추가됨)", inline=False)
                        for attachment in after.attachments:
                            if self.attachment_name(attachment) == "사진":
                                embed.set_image(url=attachment)
                                image = True
                                break
                if after.stickers != before.stickers:
                    if len(after.stickers) > 0 and len(before.stickers) > 0:
                        embed.add_field(name="스티커", value=", ".join([
                            "[{1}]({0})".format(
                                sticker.url,
                                sticker.name if sticker.name is not None else "스티커" + "({0}}".format(sticker.id)
                                if sticker.id is not None else ""
                            ) for sticker in before.stickers
                        ]) + " → " + ", ".join([
                            "[{1}]({0})".format(
                                sticker.url,
                                sticker.name if sticker.name is not None else "스티커" + "({0}}".format(sticker.id)
                                if sticker.id is not None else ""
                            ) for sticker in after.stickers
                        ]), inline=False)
                        if not image:
                            for sticker in after.stickers:
                                if self.attachment_name(sticker.url) == "사진":
                                    embed.set_image(url=sticker.url)
                                    break
                    elif len(after.stickers) == 0 and len(before.stickers) > 0:
                        embed.add_field(name="스티커", value=", ".join([
                            "[{1}]({0})".format(
                                sticker.url,
                                sticker.name if sticker.name is not None else "스티커" + "({0}}".format(sticker.id)
                                if sticker.id is not None else ""
                            ) for sticker in before.stickers
                        ]) + " (삭제됨)", inline=False)
                        if not image:
                            for attachment in before.stickers:
                                if self.attachment_name(attachment) == "사진":
                                    embed.set_image(url=attachment)
                                    break
                    elif len(after.stickers) > 0 and len(before.stickers) == 0:
                        embed.add_field(name="스티커", value=", ".join([
                            "[{1}]({0})".format(
                                sticker.url,
                                sticker.name if sticker.name is not None else "스티커" + "({0}}".format(sticker.id)
                                if sticker.id is not None else ""
                            ) for sticker in after.stickers
                        ]) + " (추가됨)", inline=False)
                        if not image:
                            for attachment in after.stickers:
                                if self.attachment_name(attachment) == "사진":
                                    embed.set_image(url=attachment)
                                    break
                embed.add_field(name="보낸 날짜", value="`{0}`".format(before.created_at), inline=True)
            elif cached_message is not None:
                if cached_message.author.bot:
                    return
                image = False
                embed.add_field(
                    name="사용자", value="{0}#{1}({2})".format(
                        cached_message.author.name, cached_message.author.discriminator, cached_message.author.id
                    ),
                    inline=False
                )
                embed.add_field(name="보낸 날짜", value="`{0}`".format(cached_message.created_at), inline=True)
                if cached_message.edited_at is not None:
                    embed.add_field(name="수정 날짜", value="`{0}`".format(cached_message.edited_at), inline=True)
            else:
                return
            if after.edited_at is not None:
                embed.add_field(
                    name="수정 날짜",
                    value="`{0}`".format(after.edited_at.strftime("%Y-%m-%d %H:%M:%S")),
                    inline=True
                )
            embed.timestamp = datetime.now(tz=timezone("UTC"))
            channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=log_activation.message_log_channel)
            await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_logging_message_delete(self, message: Optional[DatabaseMessage], raw: MessageDelete):
        database = Database(bot=self.bot, guild=raw.guild)
        if not database.get_activation("logging"):
            return
        log_activation = database.get_data(table="logging")
        if not log_activation.MESSAGE_DELETE or not log_activation.MESSAGE:
            return

        state: ConnectionState = getattr(self.bot, "_connection")

        if log_activation.message_log_channel_id is not None:
            cached_message: Optional[discord.Message] = getattr(state, "_get_message")(raw.id)
            embed = copy.deepcopy(self.embed)
            embed.title = embed.title.format("메시지 삭제")
            if message is not None:
                if message.author_bot:
                    return
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
                            self.attachment_name(attachment)
                        ) for attachment in message.attachments
                    ]), inline=False)
                    for attachment in message.attachments:
                        if self.attachment_name(attachment) == "사진":
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
                            if self.attachment_name(sticker.url) == "사진":
                                embed.set_image(url=sticker.url)
                                break
                embed.add_field(name="보낸 날짜", value="`{0}`".format(message.created_at), inline=True)
                if message.edited_at is not None:
                    embed.add_field(name="수정 날짜", value="`{0}`".format(message.edited_at), inline=True)
            elif cached_message is not None:
                if cached_message.author.bot:
                    return
                image = False
                embed.add_field(
                    name="사용자", value="{0}#{1}({2})".format(
                        cached_message.author.name, cached_message.author.discriminator, cached_message.author.id
                    ),
                    inline=False
                )
                if cached_message.content != "" and cached_message.content is not None:
                    embed.add_field(name="내용", value="{0}".format(cached_message.content), inline=False)
                if len(cached_message.attachments) > 0:
                    embed.add_field(name="파일", value=", ".join([
                        "[{1}]({0})".format(
                            attachment.url,
                            self.attachment_name(attachment.filename)
                        ) for attachment in cached_message.attachments
                    ]), inline=False)
                    for attachment in cached_message.attachments:
                        if self.attachment_name(attachment.filename) == "사진":
                            embed.set_image(url=attachment.filename)
                            image = True
                            break
                if len(cached_message.stickers) > 0:
                    embed.add_field(name="스티커", value=", ".join([
                        "[{1}]({0})".format(
                            sticker.url,
                            sticker.name
                        ) for sticker in cached_message.stickers
                    ]), inline=False)
                    if not image:
                        for sticker in cached_message.stickers:
                            if self.attachment_name(sticker.url) == "사진":
                                embed.set_image(url=sticker.url)
                                break
                embed.add_field(name="보낸 날짜", value="`{0}`".format(cached_message.created_at), inline=True)
                if message.edited_at is not None:
                    embed.add_field(name="수정 날짜", value="`{0}`".format(cached_message.edited_at), inline=True)
            else:
                return
            embed.timestamp = datetime.now(tz=timezone("UTC"))
            channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=log_activation.message_log_channel)
            await channel.send(embed=embed)
        return


def setup(client):
    client.add_cog(LoggingReceive(client))
