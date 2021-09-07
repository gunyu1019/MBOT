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
from typing import Union

from config.config import parser
from module import commands as _command
from module.interaction import SlashContext
from module.components import ActionRow
from module.message import MessageSendable, MessageCommand
from utils.convert import Convert
from utils.database import Database


class Command:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @_command.command(name="티켓", permission=1, interaction=False)
    async def ticket(self, ctx: Union[SlashContext, MessageCommand]):
        option1 = None
        print(ctx.options)
        if isinstance(ctx, SlashContext):
            option1 = ctx.options.get("종류")
        elif isinstance(ctx, Message) and len(ctx.options) > 0:
            option1 = ctx.options[0]

        if option1 == "불러오기":
            database = Database(bot=self.bot, guild=ctx.guild)
            if not database.get_activation("ticket"):
                return
            data = database.get_data("ticket")
            if data.channel_id is None or data.message is None:
                return
            convert = Convert(guild=ctx.guild)
            channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=data.channel)
            await channel.send(
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
        elif option1 == "닫기":
            self.bot.dispatch("ticket_close", ctx)
        return


def setup(client):
    return Command(client)
