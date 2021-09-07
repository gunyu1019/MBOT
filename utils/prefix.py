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

import pymysql
import json

from utils.database import Database
from config.config import parser

default_prefixes = list(json.loads(parser.get("DEFAULT", "default_prefixes")))


def get_prefix(bot, ctx):
    guild = ctx.guild
    if guild:
        guild_st = Database(bot=bot, guild=guild)
        if guild_st.check_data(table="guildSetting"):
            result = guild_st.get_data("guildSetting").prefix
        else:
            result = default_prefixes[0]
        return [result]
    else:
        return default_prefixes


def set_prefix(bot, guild, prefix):
    if guild:
        guild_st = Database(bot=bot, guild=guild)
        guild_st.set_data(table="guildSetting", data={"prefix": prefix})
    return
