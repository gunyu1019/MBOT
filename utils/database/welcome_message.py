import discord
import pymysql

from .database import DatabaseBase


class WelcomeMessage(DatabaseBase):
    def __init__(self, bot: discord.Client, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        super().__init__(guild=guild)

    def get_data(self):
        return self._get_data(table="welcomeMessage")

    def check_data(self):
        return self._check_data(table="welcomeMessage")
