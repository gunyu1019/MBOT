"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
import logging

import discord
from discord.ext import commands
from typing import Union

from module.interaction import ComponentsContext, InteractionContext
from module.message import Message
from utils.convert import Convert
from utils.database import Database
from utils.directory import directory
from utils.models import Ticket

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(f"{directory}/data/ticket.json", "r", encoding='utf-8') as file:
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

    @commands.Cog.listener()
    async def on_ticket(self, component: ComponentsContext):
        database = Database(bot=self.bot, guild=component.guild)
        if not database.get_activation("ticket"):
            return
        data = database.get_data("ticket")
        if component.author.id in self.ticket:
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
            return

        convert = Convert(guild=component.guild, member=component.author)
        self.ticket[component.author.id] = (channel.id, data.data)
        if data.comment is not None and data.comment != {}:
            if data.mode == 1:
                await component.author.send(
                    content=convert.convert_content(
                        data.comment.get("content")
                    ),
                    embed=convert.convert_embed(
                        data.comment.get("embed", {})
                    )
                )
            else:
                await channel.send(
                    content=convert.convert_content(
                        data.comment.get("content")
                    ),
                    embed=convert.convert_embed(
                        data.comment.get("embed", {})
                    )
                )
        await component.send(content="티켓이 열렸습니다.", hidden=True)
        with open(f"{directory}/data/ticket.json", "w", encoding='utf-8') as file:
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
    async def on_ticket_close(self, data: Union[Message, InteractionContext, ComponentsContext]):
        database = Database(bot=self.bot, guild=data.guild)
        data = database.get_data("ticket")
        author_id = None
        for ticket in self.ticket.keys():
            if data.channel in self.ticket[ticket]:
                author_id = ticket
                break
        if author_id is None:
            return
        author = data.guild.get_member(author_id)

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
            with open(f"{directory}/data/ticket/{data.channel_id}.txt", "w", encoding='utf-8') as file:
                file.write(logging_data)
            d_file = discord.File(f"{directory}/data/ticket/{data.channel_id}.txt")
            embed = discord.Embed(title="Ticket Logging", colour=0x0080ff)
            embed.add_field(name="Opener", value=author, inline=True)
            embed.add_field(name="Closer", value=data.author, inline=True)
            await logging_channel.send(embed=embed, files=d_file)
        await data.channel.delete()
        self.ticket.pop(author_id)
        with open(f"{directory}/data/ticket.json", "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return


def setup(client):
    client.add_cog(SocketReceive(client))
