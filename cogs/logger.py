import copy
import logging
from datetime import datetime
from typing import Optional, List, Union

import discord
from discord.ext import commands
from discord.state import ConnectionState
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
            image = False
            if before is None:
                before = cached_message

            if before is None or \
                (getattr(before, "author", 0) if isinstance(before, discord.Message)
                    else before.author_id) == self.bot.user.id:
                return
            embed.title = embed.title.format("메시지 수정")
            if before.content != "" and before.content is not None:
                embed.add_field(name="변경 전 내용", value="{0}".format(before.content), inline=True)
            if after.content != "" and after.content is not None:
                embed.add_field(name="변경 후 내용", value="{0}".format(after.content), inline=True)
            embed.add_field(name="메시지 위치", value="[링크]({0})".format(after.jump_url), inline=True)
            if isinstance(before, discord.Message):
                embed.add_field(
                    name="사용자", value="{0}#{1}({2})".format(
                        before.author.name, before.author.discriminator, before.author.id
                    ),
                    inline=False
                )
            elif isinstance(before, DatabaseMessage):
                embed.add_field(
                    name="사용자", value="{0}#{1}({2})".format(
                        before.author_name, before.author_tag, before.author_id
                    ),
                    inline=False
                )
            if [
                attachment.url for attachment in after.attachments
            ] != [
                attachment.url if not isinstance(before, DatabaseMessage)
                else attachment for attachment in before.attachments
            ]:
                if len(after.attachments) > 0 and len(before.attachments) > 0:
                    embed.add_field(name="파일", value=", ".join([
                        "[{1}]({0})".format(
                            attachment.url if isinstance(attachment, discord.Attachment) else attachment,
                            self.attachment_name(
                                attachment.filename if isinstance(attachment, discord.Attachment) else attachment
                            )
                        ) for attachment in before.attachments
                    ]) + " ▶ " + ", ".join([
                        "[{1}]({0})".format(
                            attachment.url,
                            self.attachment_name(attachment.url)
                        ) for attachment in after.attachments
                    ]), inline=False)
                    embed_upload_file = after
                elif len(before.attachments) > 0:
                    embed.add_field(name="파일", value=", ".join([
                        "[{1}]({0}) (삭제됨)".format(
                            attachment.url if isinstance(attachment, discord.Attachment) else attachment,
                            self.attachment_name(
                                attachment.filename if isinstance(attachment, discord.Attachment) else attachment
                            )
                        ) for attachment in before.attachments
                    ]), inline=False)
                    embed_upload_file = before
                elif len(after.attachments) > 0:
                    embed.add_field(name="파일", value=", ".join([
                        "[{1}]({0})".format(
                            attachment.url,
                            self.attachment_name(attachment.url)
                        ) for attachment in after.attachments
                    ]), inline=False)
                    embed_upload_file = after
                else:
                    raise TypeError("Attachment can't -1")
                for attachment in getattr(embed_upload_file, "attachments", []):
                    if self.attachment_name(
                            attachment if isinstance(embed_upload_file, DatabaseMessage) else attachment.url
                    ) == "사진":
                        embed.set_image(
                            url=attachment if isinstance(embed_upload_file, DatabaseMessage) else attachment.url
                        )
                        image = True
                        break
            if after.stickers != before.stickers:
                if len(after.stickers) > 0 and len(before.stickers) > 0:
                    embed.add_field(name="스티커", value=", ".join([
                        "[{1}]({0})".format(
                            stickers.name,
                            self.attachment_name(stickers.url)
                        ) for stickers in before.stickers
                    ]) + " ▶ " + ", ".join([
                        "[{1}]({0})".format(
                            stickers.name,
                            self.attachment_name(stickers.url)
                        ) for stickers in after.stickers
                    ]), inline=False)
                    embed_upload_file = after
                elif len(before.stickers) > 0:
                    embed.add_field(name="스티커", value=", ".join([
                        "[{1}]({0}) (삭제됨)".format(
                            stickers.name,
                            self.attachment_name(stickers.url)
                        ) for stickers in before.stickers
                    ]), inline=False)
                    embed_upload_file = before
                elif len(after.stickers) > 0:
                    embed.add_field(name="스티커", value=", ".join([
                        "[{1}]({0})".format(
                            stickers.name,
                            self.attachment_name(stickers.url)
                        ) for stickers in after.stickers
                    ]), inline=False)
                    embed_upload_file = after
                else:
                    raise TypeError("stickers can't -1")
                if not image:
                    for stickers in getattr(embed_upload_file, "stickers", []):
                        if self.attachment_name(stickers.url) == "사진":
                            embed.set_image(url=stickers.url)
                            break
            embed.add_field(
                name="보낸 날짜", value="<t:{0}:R>".format(int(before.created_at.timestamp()) + 32400), inline=True
            )
            if after.edited_at is not None:
                embed.add_field(
                    name="수정 날짜", value="<t:{0}:R>".format(int(after.edited_at.timestamp())), inline=True
                )
            channel = MessageSendable(
                state=getattr(self.bot, "_connection"), channel=log_activation.message_log_channel
            )
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
                embed.add_field(
                    name="보낸 날짜", value="<t:{0}:R>".format(int(message.created_at.timestamp()) + 32400), inline=True
                )
                if message.edited_at is not None:
                    embed.add_field(
                        name="수정 날짜", value="<t:{0}:R>".format(int(message.edited_at.timestamp())), inline=True
                    )
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
                embed.add_field(
                    name="보낸 날짜", value="<t:{0}:R>".format(int(cached_message.created_at.timestamp()) + 32400), inline=True
                )
                if cached_message.edited_at is not None:
                    embed.add_field(
                        name="수정 날짜", value="<t:{0}:R>".format(int(cached_message.edited_at.timestamp())), inline=True
                    )
            else:
                return
            embed.timestamp = datetime.now(tz=timezone("UTC"))
            channel = MessageSendable(
                state=getattr(self.bot, "_connection"),
                channel=log_activation.message_log_channel
            )
            await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_logging_message_delete_bulk(self, message: Optional[list], raw: MessageDelete):
        database = Database(bot=self.bot, guild=raw.guild)
        if not database.get_activation("logging"):
            return
        log_activation = database.get_data(table="logging")
        if not log_activation.MESSAGE_DELETE or not log_activation.MESSAGE:
            return

        state: ConnectionState = getattr(self.bot, "_connection")

        if log_activation.message_log_channel_id is not None:
            popping = 0
            for index, _message in enumerate(message[:]):
                if isinstance(_message, int):
                    cached_message: Optional[discord.Message] = getattr(state, "_get_message")(_message)
                    if cached_message is not None:
                        message[index - popping] = cached_message
                    elif cached_message is None:
                        message.pop(index - popping)
                        popping += 1
            embed = copy.deepcopy(self.embed)
            embed.title = embed.title.format("메시지 대량 삭제")
            authors = {}
            min_timestamp = datetime.now().timestamp()
            max_timestamp = 0
            for _message in message:
                timestamp = int(_message.created_at.timestamp()) + 32400
                if min_timestamp > timestamp:
                    min_timestamp = timestamp
                if max_timestamp < timestamp:
                    max_timestamp = timestamp
                if _message.author.id not in authors:
                    authors[_message.author.id] = [_message.author, 0]
                authors[_message.author.id][1] += 1
            embed.add_field(
                name="사용자", value="\n".join("* {0}#{1}({2}): {3}개".format(
                    authors[author][0].name, authors[author][0].discriminator, author, authors[author][1]
                ) for author in authors.keys()),
                inline=False
            )
            embed.add_field(
                name="보낸 시간",
                value=("<t:{0}> - <t:{1}>".format(min_timestamp, max_timestamp)) if min_timestamp != max_timestamp
                else ("<t:{0}>".format(min_timestamp)),
                inline=False
            )

            embed.timestamp = datetime.now(tz=timezone("UTC"))
            channel = MessageSendable(
                state=getattr(self.bot, "_connection"),
                channel=log_activation.message_log_channel
            )
            await channel.send(embed=embed)
        return


def setup(client):
    client.add_cog(LoggingReceive(client))
