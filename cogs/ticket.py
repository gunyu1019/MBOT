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

import discord
import logging
from discord.ext import commands

from module.interaction import ComponentsContext
from utils.database import GuildSetting, Ticket

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def convert_template(name: str, guild: discord.Guild, member: discord.Member, **kwargs):
        return name.format(
            guild=guild.name,
            guild_id=guild.id,
            member=str(member),
            member_name=member.name,
            member_tag=member.discriminator,
            member_id=member.id,
            count=kwargs.get("count")
        )

    @commands.Cog.listener()
    async def on_ticket(self, component: ComponentsContext):
        guild_st = GuildSetting(bot=self.bot, guild=component.guild)
        if not guild_st.check_func("ticket"):
            return
        ticket_st = Ticket(bot=self.bot, guild=component.guild)
        data = ticket_st.get_data()

        count = None
        if '{count}' in data.template:
            cut_names = data.template.split("{count}")
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
        await data.category.create_text_channel(
            name=self.convert_template(
                name=data.template,
                guild=component.guild,
                member=component.author,
                count=count
            ),
            category=data.category,
            overwrites={
                component.author: discord.PermissionOverwrite(
                    read_message=True,
                    read_message_history=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    view_channel=True
                ),
                component.guild.default_role: discord.PermissionOverwrite(
                    read_message=False,
                    read_message_history=False,
                    send_messages=False,
                    view_channel=False
                ),
            }
        )
        return


def setup(client):
    client.add_cog(SocketReceive(client))
