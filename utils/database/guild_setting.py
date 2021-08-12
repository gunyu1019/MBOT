import discord
import pymysql

from .database import get_database


class GuildSetting:
    def __init__(self, bot: discord.Client, guild: discord.Guild):
        self.bot = bot
        self.guild = guild

    def get_data(self):
        if self.guild:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql_command = pymysql.escape_string("select * from guildSetting where id=%s")
            cur.execute(sql_command, self.guild.id)
            result = cur.fetchone()
            connect.close()
            return result

    def check_data(self):
        if self.guild:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql_command = pymysql.escape_string("select EXISTS (select * from guildSetting where id=%s) as success")
            cur.execute(sql_command, self.guild.id)
            tf = cur.fetchone().get('success', False)
            connect.close()
            return bool(tf)
        return False

    def set_data(self, datas: dict):
        if self.guild:
            setup = [name for name in datas.keys()]
            args = [self.guild.id]
            for data in datas.keys():
                args.append(datas.get(data))
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            if self.check_data():
                _setup = [f"{name}=%s" for name in setup]
                sql_command = pymysql.escape_string(
                    f"update guildSetting set {' '.join(_setup)} where id=%s"
                )
            else:
                sql_command = pymysql.escape_string(
                    f"insert into guildSetting(prefix, id) value (%s{', %s' * len(setup)})"
                )
            cur.execute(sql_command, tuple(args))
            connect.commit()
            connect.close()

    def check_func(self, mode: str):
        data = self.get_data()
        return bool(data.get(mode, False))
