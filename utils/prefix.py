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

from utils.database import get_database
from config.config import parser

default_prefixes = list(json.loads(parser.get("DEFAULT", "default_prefixes")))


def get_prefix(_, ctx):
    guild = ctx.guild
    if guild:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_prefix = pymysql.escape_string("select prefix from guildSetting where id=%s")
        try:
            cur.execute(sql_prefix, guild.id)
            prefix = cur.fetchone()
            if prefix is not None:
                result = prefix.get('prefix')
            else:
                result = default_prefixes[0]
        except pymysql.err.InternalError:
            result = default_prefixes[0]
        connect.close()
        return [result]
    else:
        return default_prefixes


def check_prefix(_, guild):
    if guild is not None:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_prefix = pymysql.escape_string("select EXISTS (select prefix from guildSetting where id=%s) as success")
        cur.execute(sql_prefix, guild.id)
        tf = cur.fetchone()['success']
        connect.close()
        return bool(tf)


def set_prefix(bot, guild, prefix):
    if guild is not None:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        if check_prefix(bot, guild):
            sql_prefix = pymysql.escape_string("update guildSetting set prefix=%s where id=%s")
        else:
            sql_prefix = pymysql.escape_string("insert into guildSetting(prefix, id) value (%s, %s)")
        cur.execute(sql_prefix, (prefix, guild.id))
        connect.commit()
        connect.close()
