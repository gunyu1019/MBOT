import discord
import pymysql

from .database import get_database


class WelcomeMessage:
    def __init__(self, bot: discord.Client, guild: discord.Guild):
        self.bot = bot
        self.guild = guild

    def get_data(self):
        if self.guild:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql_command = pymysql.escape_string("select * from welcomeMessage where id=%s")
            cur.execute(sql_command, self.guild.id)
            result = cur.fetchone()
            connect.close()
            return result

    def check_data(self):
        if self.guild:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql_command = pymysql.escape_string("select EXISTS (select * from welcomeMessage where id=%s) as success")
            cur.execute(sql_command, self.guild.id)
            tf = cur.fetchone().get('success', False)
            connect.close()
            return bool(tf)
        return False
