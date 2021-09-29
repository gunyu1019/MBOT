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
from module.interaction import ApplicationContext
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

    @_command.command(name="경고", permission=1)
    async def warning(self, ctx: Union[ApplicationContext, MessageCommand]):
        return

    @_command.command(name="밴", permission=1)
    async def ban(self, ctx: Union[ApplicationContext, MessageCommand]):
        return

    @_command.command(name="언밴", permission=1)
    async def unban(self, ctx: Union[ApplicationContext, MessageCommand]):
        return

    @_command.command(name="차단", permission=1)
    async def kick(self, ctx: Union[ApplicationContext, MessageCommand]):
        return


def setup(client):
    return Command(client)
