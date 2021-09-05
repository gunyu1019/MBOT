import json
import logging
import os

import discord
from discord.ext import commands
from typing import Union, List

from module.interaction import ComponentsContext, InteractionContext
from module.message import Message, MessageSendable
from utils.convert import Convert
from utils.database import Database
from utils.directory import directory
from utils.models import Ticket

logger = logging.getLogger(__name__)
DBS = None


class TicketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(os.path.join(directory, "data", "ticket.json"), "r", encoding='utf-8') as file:
            self.ticket = json.load(fp=file)

    @staticmethod
    def convert_template(name: str, guild: discord.Guild, member: discord.Member, **kwargs):
        return name.format(
            guild=guild.name,
            guild_id=guild.id,
            member=str(member),
            member_name=member.name,
            member_tag=member.discriminator,
            member_id=member.id,
            number=kwargs.get("count")
        )

    @property
    def get_all_ticket(self) -> List[dict]:
        tickets = []
        for ticket in self.ticket.values():
            tickets.extend(ticket)
        return tickets

    @staticmethod
    async def send(message: Message, send_func):
        files = []
        if len(message.attachments) != 0:
            for attachment in message.attachments:
                file = await attachment.to_file()
                files.append(file)
        msg = await send_func(
            content="**{author}**: {message}".format(author=message.author, message=message.content),
            files=None if len(message.attachments) == 0 else files
        )
        await message.add_reaction("\U00002705")
        return msg

    @commands.Cog.listener()
    async def on_ticket(self, context: ComponentsContext):
        database = Database(bot=self.bot, guild=context.guild)
        if not database.get_activation("ticket"):
            return
        data = database.get_data("ticket")
        if str(context.guild.id) not in self.ticket:
            self.ticket[str(context.guild.id)] = []

        if data.mode == 1:
            for guild_id in self.ticket.keys():
                for check_ticket in self.ticket[guild_id]:
                    if context.author.id == check_ticket.get("author") and check_ticket.get("mode") == 1:
                        if str(context.guild.id) == guild_id:
                            await context.send(content="이미 티켓이 열려 있습니다!", hidden=True)
                            return
                        await context.send(
                                content="다른 서버의 티켓이 열려 있어, 해당 서버의 티켓을 사용할 수 없습니다.",
                                hidden=True
                        )
                        return
        else:
            for check_ticket in self.ticket[str(context.guild.id)]:
                if context.author.id == check_ticket.get("author"):
                    await context.send(content="이미 티켓이 열려 있습니다!", hidden=True)
                    return

        count = None
        if '{number}' in data.template:
            cut_names = data.template.split("{number}")
            opened_number = []
            if len(cut_names) > 1:
                front_name = cut_names[0]
                end_name = cut_names[1]
                channels = []
                if data.mode == 0 or data.mode == 1:
                    channels = data.category.channels
                elif data.mode == 2 or data.mode == 3:
                    channels = data.channel.threads

                for channel in channels:
                    number = channel.name.lstrip(front_name).rstrip(end_name)
                    if number.isdecimal():
                        opened_number.append(int(number))
                for number in range(1, len(data.category.channels)):
                    if number not in opened_number:
                        count = number
                        break

        if data.mode == 0:
            channel = await data.category.create_text_channel(
                name=self.convert_template(
                    name=data.template,
                    guild=context.guild,
                    member=context.author,
                    count=count
                ),
                overwrites={
                    self.bot.user: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        view_channel=True
                    ),
                    context.author: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        view_channel=True
                    ),
                    context.guild.default_role: discord.PermissionOverwrite(
                        read_message_history=False,
                        send_messages=False,
                        view_channel=False
                    )
                },
                topic=data.topic
            )
        elif data.mode == 1:
            channel = await data.category.create_text_channel(
                name=self.convert_template(
                    name=data.template,
                    guild=context.guild,
                    member=context.author,
                    count=count
                ),
                overwrites={
                    context.guild.default_role: discord.PermissionOverwrite(
                        read_message_history=False,
                        send_messages=False,
                        view_channel=False
                    ),
                    self.bot.user: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        view_channel=True
                    )
                }
            )
        elif data.mode == 2:
            channel = await data.channel.create_thread(
                name=self.convert_template(
                    name=data.template,
                    guild=context.guild,
                    member=context.author,
                    count=count
                ),
                type=discord.ChannelType.private_thread
            )
            await channel.add_user(context.author)
        elif data.mode == 3:
            channel = await data.channel.create_thread(
                name=self.convert_template(
                    name=data.template,
                    guild=context.guild,
                    member=context.author,
                    count=count
                ),
                type=discord.ChannelType.public_thread
            )
            await channel.add_user(context.author)
        else:
            # Not Worked
            return

        convert = Convert(guild=context.guild, member=context.author)
        self.ticket[str(context.guild.id)].append({
            "type": "ticket",
            "channel": channel.id,
            "mode": data.mode,
            "guild": context.guild.id,
            "author": context.author.id,
            "setting": data.data
        })

        if data.comment is not None and data.comment != {}:
            if data.mode == 0 or data.mode == 2 or data.mode == 3:
                _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=data.channel)
                await _channel.send(
                    content=convert.convert_content(
                        data.comment.get("content")
                    ),
                    embed=convert.convert_embed(
                        data.comment.get("embed", {})
                    )
                )
            elif data.mode == 1:
                await context.author.send(
                    content=convert.convert_content(
                        data.comment.get("content")
                    ),
                    embed=convert.convert_embed(
                        data.comment.get("embed", {})
                    )
                )
        await context.send(content="티켓이 열렸습니다.", hidden=True)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)

    @commands.Cog.listener()
    async def on_interaction_message(self, message: Message):
        if message.author.bot:
            return

        if message.channel.type == discord.ChannelType.private:
            all_tickets = self.get_all_ticket
            ticket = None
            for _data in all_tickets:
                if _data.get("author") == message.author.id and _data.get("mode") == 1:
                    ticket = _data
            if ticket is None:
                return

            data = Ticket(data=ticket.get("setting"), bot=self.bot)
            channel_id = ticket.get("channel")
            channel = data.guild.get_channel(channel_id)
            await self.send(message, channel.send)
        elif message.channel.type == discord.ChannelType.text:
            ticket = None
            for _data in self.ticket.get(str(message.guild.id), []):
                if _data.get("channel") == message.channel.id and _data.get("mode") == 1:
                    ticket = _data
            if ticket is None:
                return
            author_id = ticket.get("author")
            author = message.guild.get_member(author_id)
            await self.send(message, author.send)
        return

    @commands.Cog.listener()
    async def on_ticket_close(self, context: Union[Message, InteractionContext, ComponentsContext]):
        ticket = None
        guild = context.guild
        if context.channel.type == discord.ChannelType.private:
            for guild_data in self.ticket.keys():
                for _data in self.ticket[guild_data]:
                    if _data.get("author") == context.author.id and _data.get("mode") == 1:
                        ticket = _data
                        guild = self.bot.get_guild(int(guild_data))
            data = Ticket(data=ticket.get("setting"), bot=self.bot)
        elif context.channel.type == discord.ChannelType.text:
            database = Database(bot=self.bot, guild=context.guild)
            data = database.get_data("ticket")

            all_tickets = self.ticket.get(str(context.guild.id), [])
            for _data in all_tickets:
                if _data.get("channel") == context.channel.id:
                    ticket = _data
        if ticket is None:
            return
        author = guild.get_member(ticket.get("author"))
        channel = guild.get_channel(ticket.get("channel")) or context.guild.get_thread(ticket.get("channel"))

        if data.mode == 0:
            channel: discord.TextChannel
            await channel.set_permissions(
                author,
                overwrite=discord.PermissionOverwrite(
                    read_message_history=False,
                    send_messages=False,
                    view_channel=False
                )
            )

        if data.logging and data.logging_channel_id is not None:
            logging_data = "{guild}\n".format(guild=data.guild.name)
            async for message in channel.history(oldest_first=True):
                content = message.content
                if message.author == self.bot.user and data.mode == 1:
                    content = content.lstrip("**{author}**: ".format(author=author))

                logging_data += "[{datetime}|{author}]: {content}\n".format(
                    datetime=message.created_at.strftime("%Y-%m-%d %p %I:%M:%S"),
                    author=message.author, content=content
                )

            logging_channel = data.logging_channel
            with open(
                    os.path.join(directory, "data", "ticket", "{0}.txt".format(channel.id)),
                    "w", encoding='utf-8'
            ) as file:
                file.write(logging_data)
            d_file = discord.File(os.path.join(directory, "data", "ticket", "{0}.txt".format(channel.id)))
            embed = discord.Embed(title="Ticket Logging", colour=0x0080ff)
            embed.add_field(name="Opener", value=author, inline=True)
            embed.add_field(name="Closer", value=context.author, inline=True)
            await logging_channel.send(embed=embed, file=d_file)

        if data.mode == 2 or data.mode == 3:
            channel: discord.Thread
            await channel.edit(archived=True)
        else:
            channel: discord.TextChannel
            await channel.delete()
        position = self.ticket[str(guild.id)].index(ticket)
        self.ticket[str(guild.id)].pop(position)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return


def setup(client):
    client.add_cog(TicketReceive(client))
