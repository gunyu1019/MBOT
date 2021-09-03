import json
import logging
import os

import discord
from discord.ext import commands
from typing import Union

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

    def save_setting(self, guild: Union[discord.Guild, int], data: Ticket):
        if isinstance(guild, discord.Guild):
            guild = guild.id
        if guild not in self.ticket:
            self.ticket[guild] = []

            guild_st = data.data
            guild_st["type"] = "setting"
            self.ticket[guild].append(guild_st)
            return

        for index, _data in enumerate(self.ticket[guild]):
            if _data.get("type") == "setting":
                self.ticket.get(guild, []).update(data.data)

    @commands.Cog.listener()
    async def on_ticket(self, component: ComponentsContext):
        database = Database(bot=self.bot, guild=component.guild)
        if not database.get_activation("ticket"):
            return
        data = database.get_data("ticket")
        self.save_setting(guild=component.guild.id, data=data)
        if data.mode == 1:
            for guild_id in self.ticket.keys():
                for check_ticket in self.ticket.get(guild_id, []):
                    if component.author.id == check_ticket.get("author"):
                        if component.guild.id == guild_id:
                            await component.send(content="이미 티켓이 열려 있습니다!", hidden=True)
                            return
                        await component.send(
                                content="다른 서버의 티켓이 열려 있어, 해당 서버의 티켓을 사용할 수 없습니다.",
                                hidden=True
                        )
                        return
        else:
            for check_ticket in self.ticket.get(component.guild.id, []):
                if component.author.id == check_ticket.get("author"):
                    await component.send(content="이미 티켓이 열려 있습니다!", hidden=True)
                    return

        count = None
        if '{number}' in data.template:
            cut_names = data.template.split("{number}")
            opened_number = []
            if len(cut_names) > 1:
                front_name = cut_names[0]
                end_name = cut_names[1]
                for channel in data.category.channels:
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
                    guild=component.guild,
                    member=component.author,
                    count=count
                ),
                overwrites={
                    component.author: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        view_channel=True
                    ),
                    component.guild.default_role: discord.PermissionOverwrite(
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
                    guild=component.guild,
                    member=component.author,
                    count=count
                ),
                overwrites={
                    component.guild.default_role: discord.PermissionOverwrite(
                        read_message_history=False,
                        send_messages=False,
                        view_channel=False
                    )
                }
            )
        elif data.mode == 2:
            channel = await data.channel.create_thread(
                name=self.convert_template(
                    name=data.template,
                    guild=component.guild,
                    member=component.author,
                    count=count
                ),
                type=discord.ChannelType.private_thread
            )
        elif data.mode == 3:
            channel = await data.channel.create_thread(
                name=self.convert_template(
                    name=data.template,
                    guild=component.guild,
                    member=component.author,
                    count=count
                ),
                type=discord.ChannelType.public_thread
            )
        else:
            # Not Worked
            return

        convert = Convert(guild=component.guild, member=component.author)
        self.ticket[component.guild.id].append({"type": "ticket", "channel": channel.id, "author": component.author.id})
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
                await component.author.send(
                    content=convert.convert_content(
                        data.comment.get("content")
                    ),
                    embed=convert.convert_embed(
                        data.comment.get("embed", {})
                    )
                )
        await component.send(content="티켓이 열렸습니다.", hidden=True)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)

    @commands.Cog.listener()
    async def on_interaction_message(self, message: Message):
        if message.author.id not in self.ticket or message.channel.type != discord.DMChannel:
            return
        channel_id, _data = self.ticket.get(message.author.id)
        data = Ticket(data=_data, bot=self.bot)
        if data.mode != 1:
            return
        channel = data.guild.get_channel(channel_id)
        files = []
        if len(message.attachments) != 0:
            for attachment in message.attachments:
                file = await attachment.to_file()
                files.append(file)
        await channel.send(
            content="**{author}**: {message}".format(author=message.author, message=message.content),
            files=files
        )
        await message.add_reaction("\U00002705")
        return

    @commands.Cog.listener()
    async def on_ticket_close(self, context: Union[Message, InteractionContext, ComponentsContext]):
        database = Database(bot=self.bot, guild=context.guild)
        data = database.get_data("ticket")
        self.save_setting(guild=context.guild, data=data)

        author_id = None
        for ticket in self.ticket.keys():
            if data.channel in self.ticket[ticket]:
                author_id = ticket
                break
        if author_id is None:
            return
        author = context.guild.get_member(author_id)

        if data.mode == 0:
            data.channel.set_permission(
                author,
                overwrite=discord.PermissionOverwrite(
                    read_message=False,
                    read_message_history=False,
                    send_messages=False,
                    view_channel=False
                )
            )
        # elif data.mode == 2 or data.mode == 3:

        if data.logging and data.logging_channel_id is not None:
            logging_data = "{guild}\n".format(guild=data.guild.name)
            async for message in data.channel.history(oldest_first=True):
                content = message.content
                if message.author == self.bot.user and data.mode == 1:
                    content = content.lstrip("**{author}**: ".format(author=author))

                logging_data += "[{datetime}|{author}]: {content}".format(
                    datetime=message.created_at.strftime("%Y-%m-%d %p %I:%M:%S"),
                    author=message.author, content=content
                )

            logging_channel = data.logging_channel
            with open(
                    os.path.join(directory, "data", "ticket", "{0}.txt".format(data.channel.id)),
                    "w", encoding='utf-8'
            ) as file:
                file.write(logging_data)
            d_file = discord.File(os.path.join(directory, "data", "ticket", "{0}.txt".format(data.channel.id)))
            embed = discord.Embed(title="Ticket Logging", colour=0x0080ff)
            embed.add_field(name="Opener", value=author, inline=True)
            embed.add_field(name="Closer", value=data.author, inline=True)
            await logging_channel.send(embed=embed, files=d_file)
        if data.mode == 2 and data.mode == 3:
            await data.channel.edit(archived=True)
        else:
            await data.channel.delete()
        self.ticket.pop(author_id)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return


def setup(client):
    client.add_cog(TicketReceive(client))
