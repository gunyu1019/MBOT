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
import logging
from config.config import parser
from utils import models

log = logging.getLogger(__name__)


def get_database(database=None):
    for tries in ['MySQL1', 'MySQL2']:
        host = parser.get(tries, 'host')
        user = parser.get(tries, 'user')
        password = parser.get(tries, 'pass')
        if database is None:
            database = parser.get(tries, 'database')
        encoding = parser.get(tries, 'encoding')

        try:
            log.debug(f"{tries} section을 통하여 로그인을 시도합니다.")
            connection = pymysql.connect(host=host, user=user, password=password, db=database, charset=encoding)
        except pymysql.err.OperationalError:
            continue
        return connection


class Database:
    def __init__(self, guild, bot):
        self.guild = guild
        self.bot = bot

    def _get_model(self, data: dict, table: str):
        if data is not None:
            if table == "authorized":
                return models.Authorized(data, self.bot)
            elif table == "ticket":
                return models.Ticket(data, self.bot)
            elif table == "welcomeMessage":
                return models.WelcomeMessage(data, self.bot)
            elif table == "guildSetting":
                return models.GuildSetting(data, self.bot)
        return data

    def get_data(self, table: str, key: str = None):
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_command = pymysql.escape_string(f"select * from {table} where id=%s")
        cur.execute(sql_command, key or self.guild.id)
        result = cur.fetchone()
        connect.close()
        return self._get_model(result, table)

    def check_data(self, table: str, key: str = None):
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_command = pymysql.escape_string(f"select EXISTS (select * from {table} where id=%s) as success")
        cur.execute(sql_command, key or self.guild.id)
        tf = cur.fetchone().get('success', False)
        connect.close()
        return bool(tf)

    def set_data(self, table: str, data: dict, key: str = None):
        setup = [name for name in data.keys()]
        args = []
        for d in data.keys():
            args.append(data.get(d))
        args.append(key or self.guild.id)
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        if self.check_data(table=table, key=key):
            _setup = [f"{name}=%s" for name in setup]
            sql_command = pymysql.escape_string(
                f"update {table} set {', '.join(_setup)} where id=%s"
            )
        else:
            sql_command = pymysql.escape_string(
                f"insert into {table}({', '.join(setup)}, id) value (%s{', %s' * (len(args) -1 )})"
            )
        cur.execute(sql_command, tuple(args))
        connect.commit()
        connect.close()

    def get_activation(self, name: str):
        return bool(
            getattr(self.get_data("guildSetting"), name, 0)
        )

    def get_message(self, message_id: int, channel_id: int):
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_command = pymysql.escape_string("select * from message where id=%s and channel_id=%s")
        cur.execute(sql_command, (message_id, channel_id))
        result = cur.fetchone()
        connect.close()
        return result

    @staticmethod
    def check_message(message_id: int, channel_id: int):
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_command = pymysql.escape_string(
            "select EXISTS (select * from message where id=%s and channel_id=%s) as success"
        )
        cur.execute(sql_command, (message_id, channel_id))
        tf = cur.fetchone().get('success', False)
        connect.close()
        return bool(tf)

    def set_message(self, data: dict, message_id: int, channel_id: int):
        setup = [name for name in data.keys()]
        args = []

        for d in data.keys():
            args.append(data.get(d))
        args.extend([message_id, channel_id])
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        if self.check_message(message_id=message_id, channel_id=channel_id):
            _setup = [f"{name}=%s" for name in setup]
            sql_command = pymysql.escape_string(
                f"update message set {', '.join(_setup)} where id=%s and channel_id=%s"
            )
        else:
            sql_command = pymysql.escape_string(
                f"insert into message({', '.join(setup)}, id, channel_id) value (%s{', %s' * (len(args) -1 )})"
            )
        cur.execute(sql_command, tuple(args))
        connect.commit()
        connect.close()

    def delete_message(self, message_id: int, channel_id: int):
        if not self.check_message(message_id=message_id, channel_id=channel_id):
            return
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_command = pymysql.escape_string("delete from message where id=%s and channel_id=%s")
        cur.execute(sql_command, (message_id, channel_id))
        connect.commit()
        connect.close()
