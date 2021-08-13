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
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""

import discord
import logging
import json
from discord.ext import commands

from utils.database import GuildSetting, WelcomeMessage

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def convert_embed(data: dict, **kwargs):
        if data == {}:
            return
        embed = discord.Embed()
        if data.get("title") is not None:
            embed.title = data.get("title", discord.Embed.Empty)
        if data.get("description") is not None:
            embed.description = data.get("description", discord.Embed.Empty)
        if data.get("color") is not None:
            embed.colour = data.get("colour", 0)
        if data.get("fields") is not None:
            for field in data.get("fields", []):
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", "")
                )
        if data.get("thumbnail") is not None:
            if kwargs.get("member") is not None and data.get("thumbnail") == "<@AUTHOR_AVATAR>":
                member: discord.Member = kwargs.get("member")
                embed.set_thumbnail(url=member.avatar_url_as(format="png", size=1024))
            if kwargs.get("guild") is not None and data.get("thumbnail") == "<@GUILD>":
                guild: discord.Guild = kwargs.get("guild")
                icon = guild.icon_url_as(format="png", size=1024)
                embed.set_thumbnail(url=str(icon))
            else:
                embed._thumbnail = {
                    'url': str(data.get("thumbnail"))
                }
        if data.get("footer") is not None:
            if isinstance(data.get("footer"), str):
                text = data.get("footer")
                icon_url = discord.Embed.Empty
            else:
                footer = data.get("footer", {})
                text = footer.get("text", discord.Embed.Empty)
                icon_url = footer.get("icon_url", discord.Embed.Empty)
            embed.set_footer(text=text, icon_url=icon_url)
        if data.get("author") is not None:
            if isinstance(data.get("author"), str):
                text = data.get("author")
                url = discord.Embed.Empty
                icon_url = discord.Embed.Empty
            else:
                author = data.get("author", {})
                text = author.get("text", discord.Embed.Empty)
                url = author.get("url", discord.Embed.Empty)
                icon_url = author.get("icon_url", discord.Embed.Empty)
            embed.set_author(name=text, icon_url=icon_url, url=url)
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_st = GuildSetting(bot=self.bot, guild=member.guild)
        if not guild_st.check_func("welcome_message"):
            return
        welcome_st = WelcomeMessage(bot=self.bot, guild=member.guild)
        data = welcome_st.get_data()

        if data.get("welcome_message") is not None:
            channel_id = data.get("welcome_channel")
            if channel_id is None:
                return
            if isinstance(data.get("welcome_message"), str):
                welcome_msg = json.loads(data.get("welcome_message", '{}'))
            else:
                welcome_msg = data.get("welcome_message", {})

            if welcome_msg == {}:
                return
            channel = member.guild.get_channel(id=channel_id)
            await channel.send(
                content=welcome_msg.get("content"),
                embed=self.convert_embed(
                    welcome_msg.get("embed", {}),
                    member=member,
                    guild=member.guild
                )
            )

        if data.get("welcome_DMmessage") is not None:
            if isinstance(data.get("welcome_DMmessage"), str):
                welcome_msg = json.loads(data.get("welcome_DMmessage", '{}'))
            else:
                welcome_msg = data.get("welcome_DMmessage", {})

            if welcome_msg == {}:
                return
            await member.send(
                content=welcome_msg.get("content"),
                embed=self.convert_embed(
                    welcome_msg.get("embed", {}),
                    member=member,
                    guild=member.guild
                )
            )
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_st = GuildSetting(bot=self.bot, guild=member.guild)
        if not guild_st.check_func("welcome_message"):
            return
        welcome_st = WelcomeMessage(bot=self.bot, guild=member.guild)
        data = welcome_st.get_data()

        if data.get("leave_message") is not None:
            channel_id = data.get("welcome_channel")
            if channel_id is None:
                return
            if isinstance(data.get("leave_message"), str):
                leave_message = json.loads(data.get("leave_message", '{}'))
            else:
                leave_message = data.get("leave_message", {})

            if leave_message == {}:
                return
            channel = member.guild.get_channel(id=channel_id)
            await channel.send(
                content=leave_message.get("content"),
                embed=self.convert_embed(
                    leave_message.get("embed", {}),
                    member=member,
                    guild=member.guild
                )
            )
        return


def setup(client):
    client.add_cog(SocketReceive(client))
