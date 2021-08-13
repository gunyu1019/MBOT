import discord
import pymysql

from .database import DatabaseBase


class GuildSetting(DatabaseBase):
    def __init__(self, bot: discord.Client, guild: discord.Guild):
        super().__init__(guild=guild)
        self.bot = bot
        self.guild = guild

    def get_data(self):
        if self.guild:
            return self._get_data(table="logging")

    def check_data(self):
        if self.guild:
            return self._check_data(table="logging")
        return False

    def set_data(self, **kwargs):
        if self.guild:
            return self._set_data(table="logging", datas=kwargs)
        return
