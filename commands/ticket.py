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

from config.config import parser
from module import commands as _command
from module.components import ActionRow
from module.message import Channel
from utils.convert import Convert
from utils.database import Database


class Command:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.color = int(parser.get("DEFAULT", "color"), 16)

    @_command.command(name="티켓", permission=1, interaction=False)
    async def ticket(self, ctx):
        database = Database(bot=self.bot, guild=ctx.guild)
        if not database.get_activation("ticket"):
            return
        data = database.get_data("ticket")
        if data.channel_id is None or data.message is None:
            return
        convert = Convert(guild=ctx.guild)
        channel = Channel(state=getattr(self.bot, "_connection"), channel=data.channel)
        msg = await channel.send(
            content=convert.convert_content(
                data.message.get("content")
            ),
            embed=convert.convert_embed(
                data.message.get("embed", {})
            ),
            components=[ActionRow(
                components=[
                    convert.convert_button(
                        custom_id="open_ticket",
                        data=data.message.get("button", {
                            "label": "티켓 열림",
                            "style": 1
                        }),
                        emoji=data.emoji if data.emoji is not None and data.emoji != {} else {
                            "name": "\U0001F39F"
                        }
                    )
                ]
            )]
        )
        return


def setup(client):
    return Command(client)
