import discord

from .database import DatabaseBase


class Ticket(DatabaseBase):
    def __init__(self, bot: discord.Client, guild: discord.Guild):
        super().__init__(guild=guild)
        self.bot = bot
        self.guild = guild

    def get_data(self):
        if self.guild:
            return TicketReceive(self._get_data(table="ticket"), bot=self.bot)

    def check_data(self):
        if self.guild:
            return self._check_data(table="ticket")
        return False

    def set_data(self, **kwargs):
        if self.guild:
            return self._set_data(table="ticket", datas=kwargs)
        return


class TicketReceive:
    def __init__(self, data: dict, bot: discord.Client):
        self.guild_id = data.get("id")
        self.channel_id = data.get("ticket_channel")
        self.mode = data.get("ticket_mode")
        self.category_id = data.get("ticket_category")
        self.logging = bool(data.get("logging_channel"))
        self.logging_channel_id = data.get("ticket_log_id")
        self.template = data.get("ticket_name")

        self.guild: discord.Guild = bot.get_guild(id=self.guild_id)
        self.channel: discord.TextChannel = self.guild.get_channel(self.channel_id)
        self.category: discord.CategoryChannel = self.guild.get_channel(self.category_id)
        self.logging_channel: discord.TextChannel = self.guild.get_channel(self.logging_channel_id)