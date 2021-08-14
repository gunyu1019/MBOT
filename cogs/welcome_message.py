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
import json
from discord.ext import commands

from utils.database import Database

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def convert_content(msg: str, **kwargs):
        guild: discord.Guild = kwargs.get("guild")
        member: discord.Member = kwargs.get("member")
        return msg.format(
            guild=guild.name,
            guild_id=guild.id,
            member=str(member),
            member_name=member.name,
            member_tag=member.discriminator,
            member_id=member.id,
            member_count=guild.member_count,
            mention="<@{}>".format(member.id)
        )

    def convert_embed(self, data: dict, **kwargs):
        member: discord.Member = kwargs.get("member")
        guild: discord.Guild = kwargs.get("guild") or member.guild
        if data == {}:
            return
        embed = discord.Embed()
        if data.get("title") is not None:
            embed.title = self.convert_content(
                data.get("title", discord.Embed.Empty),
                member=member,
                guild=member.guild
            )
        if data.get("description") is not None:
            embed.description = self.convert_content(
                data.get("description", discord.Embed.Empty),
                member=member,
                guild=member.guild
            )
        if data.get("color") is not None:
            embed.colour = data.get("color", 0)
        if data.get("fields") is not None:
            for field in data.get("fields", []):
                embed.add_field(
                    name=self.convert_content(
                        field.get("name", ""),
                        member=member,
                        guild=member.guild
                    ),
                    value=self.convert_content(
                        field.get("value", ""),
                        member=member,
                        guild=member.guild
                    ),
                    inline=field.get("inline", "")
                )
        if data.get("thumbnail") is not None:
            print(kwargs.get("member") is not None and data.get("thumbnail") == "<@AUTHOR_AVATAR>")
            if kwargs.get("member") is not None and data.get("thumbnail") == "<@AUTHOR_AVATAR>":
                member: discord.Member = kwargs.get("member")
                embed.set_thumbnail(url=member.avatar_url_as(format="png", size=1024))
            elif kwargs.get("guild") is not None and data.get("thumbnail") == "<@GUILD>":
                icon = guild.icon_url_as(format="png", size=1024)
                embed.set_thumbnail(url=str(icon))
            else:
                embed._thumbnail = {
                    'url': str(data.get("thumbnail"))
                }
        if data.get("footer") is not None:
            if isinstance(data.get("footer"), str):
                text = self.convert_content(
                    data.get("footer"),
                    member=member,
                    guild=member.guild
                )
                icon_url = discord.Embed.Empty
            else:
                footer = data.get("footer", {})
                text = self.convert_content(
                    footer.get("text", discord.Embed.Empty),
                    member=member,
                    guild=member.guild
                )
                icon_url = footer.get("icon_url", discord.Embed.Empty)
            embed.set_footer(text=text, icon_url=icon_url)
        if data.get("author") is not None:
            if isinstance(data.get("author"), str):
                text = self.convert_content(
                    data.get("author"),
                    member=member,
                    guild=member.guild
                )
                url = discord.Embed.Empty
                icon_url = discord.Embed.Empty
            else:
                author = data.get("author", {})
                text = self.convert_content(
                    author.get("text", discord.Embed.Empty),
                    member=member,
                    guild=member.guild
                )
                url = author.get("url", discord.Embed.Empty)
                icon_url = author.get("icon_url", discord.Embed.Empty)
            embed.set_author(name=text, icon_url=icon_url, url=url)
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        database = Database(bot=self.bot, guild=member.guild)
        if not database.get_activation("welcome_message"):
            return
        data = database.get_data("WelcomeMessage")

        if data.get("welcome_message") is not None:
            channel_id = data.get("welcome_channel")
            if channel_id is None:
                return
            welcome_msg = data.welcome_message

            if welcome_msg == {}:
                return
            channel = member.guild.get_channel(channel_id)
            await channel.send(
                content=welcome_msg.get("content"),
                embed=self.convert_embed(
                    welcome_msg.get("embed", {}),
                    member=member,
                    guild=member.guild
                )
            )

        if data.welcome_DMmessage is not None:
            welcome_msg = data.welcome_DMmessage

            if welcome_msg == {}:
                return
            await member.send(
                content=self.convert_content(
                    welcome_msg.get("content"),
                    member=member,
                    guild=member.guild
                ),
                embed=self.convert_embed(
                    welcome_msg.get("embed", {}),
                    member=member,
                    guild=member.guild
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
            channel_id = data.welcome_channel_id
            if channel_id is None:
                return
            leave_message = data.leave_message

            if leave_message == {}:
                return
            channel = data.welcome_channel
            await channel.send(
                content=self.convert_content(
                    leave_message.get("content"),
                    member=member,
                    guild=member.guild
                ),
                embed=self.convert_embed(
                    leave_message.get("embed", {}),
                    member=member,
                    guild=member.guild
                )
            )
        return


def setup(client):
    client.add_cog(SocketReceive(client))
