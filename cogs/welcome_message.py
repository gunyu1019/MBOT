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

from utils.convert import Convert
from utils.database import Database

logger = logging.getLogger(__name__)
DBS = None


class WelcomeMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        database = Database(bot=self.bot, guild=member.guild)
        if not database.get_activation("welcome_message"):
            return
        data = database.get_data("WelcomeMessage")

        if data.welcome_message is not None:
            channel_id = data.welcome_channel_id
            if channel_id is None:
                return
            welcome_msg = data.welcome_message

            if welcome_msg == {}:
                return
            convert = Convert(guild=member.guild, member=member)
            channel = data.welcome_channel
            await channel.send(
                content=welcome_msg.get("content"),
                embed=convert.convert_embed(
                    welcome_msg.get("embed", {})
                )
            )

        if data.welcome_DMmessage is not None:
            welcome_msg = data.welcome_DMmessage

            if welcome_msg == {}:
                return
            convert = Convert(guild=member.guild, member=member)
            await member.send(
                content=convert.convert_content(
                    welcome_msg.get("content")
                ),
                embed=convert.convert_embed(
                    welcome_msg.get("embed", {})
                )
            )
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        database = Database(bot=self.bot, guild=member.guild)
        if not database.get_activation("welcome_message"):
            return
        data = database.get_data("welcomeMessage")

        if data.leave_message is not None:
            channel_id = data.leave_channel_id
            if channel_id is None:
                return
            leave_message = data.leave_message

            if leave_message == {}:
                return
            convert = Convert(guild=member.guild, member=member)
            channel = data.leave_channel
            await channel.send(
                content=convert.convert_content(
                    leave_message.get("content")
                ),
                embed=convert.convert_embed(
                    leave_message.get("embed", {})
                )
            )
        return


def setup(client):
    client.add_cog(WelcomeMessage(client))
