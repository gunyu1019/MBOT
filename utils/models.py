import discord
import json
import typing


class DatabaseModel:
    def __init__(self, data: dict, bot: discord.Client):
        self.data = data
        self.bot = bot

        self.guild_id = data.get("id")

    @staticmethod
    def convert_dict(data: typing.Union[str, dict]):
        if isinstance(data, str):
            return json.loads(data)
        return data

    @property
    def guild(self) -> discord.Guild:
        return self.bot.get_guild(self.guild_id)


class Authorized(DatabaseModel):
    def __init__(self, data: dict, bot: discord.Client):
        super().__init__(data, bot)

        self.robot = bool(data.get("check_robot"))
        self.robot_kick = data.get("robot_kick")
        self.user_role_id = data.get("user_role")
        self.bot_role_id = data.get("bot_role")
        self.reaction = bool(data.get("reaction"))
        self.reaction_message = self.convert_dict(data.get("reaction_commnet"))
        self.reaction_button = self.convert_dict(data.get("reaction_button"))
        self.in_out_ban = bool(data.get("ban_in_and_out"))
        self.in_out_count = int(data.get("in_and_out_count"))

    @property
    def user_role(self) -> discord.Role:
        return self.guild.get_role(self.user_role_id)

    @property
    def bot_role(self) -> discord.Role:
        return self.guild.get_role(self.bot_role_id)


class Ticket(DatabaseModel):
    def __init__(self, data: dict, bot: discord.Client):
        super().__init__(data, bot)

        self.template = data.get("ticket_name")
        self.mode = data.get("ticket_mode")
        self.channel_id = data.get("ticket_channel")
        self.category_id = data.get("ticket_category")
        self.comment = self.convert_dict(data.get("ticket_comment"))
        self.message = self.convert_dict(data.get("ticket_template"))
        self.topic = data.get("ticket_topic_template")
        self.emoji = self.convert_dict(data.get("ticket_emoji"))
        self.logging = bool(data.get("logging"))
        self.logging_channel_id = data.get("logging_channel")

    @property
    def channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.channel_id)

    @property
    def category(self) -> discord.CategoryChannel:
        return self.guild.get_channel(self.category_id)

    @property
    def logging_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.logging_channel_id)


class GuildSetting(DatabaseModel):
    def __init__(self, data: dict, bot: discord.Client):
        super().__init__(data, bot)

        self.prefix = data.get("prefix")
        self.welcome_message: bool = bool(data.get("welcome_message"))
        self.warning: bool = bool(data.get("warning"))
        self.leveling: bool = bool(data.get("leveling"))
        self.logging: bool = bool(data.get("logging"))
        self.authorized: bool = bool(data.get("authorized"))
        self.statistics: bool = bool(data.get("statistics"))
        self.ticket: bool = bool(data.get("ticket"))


class WelcomeMessage(DatabaseModel):
    def __init__(self, data: dict, bot: discord.Client):
        super().__init__(data, bot)
        self.data = data
        self.bot = bot

        self.prefix = data.get("prefix")
        self.welcome_channel_id = data.get("welcome_channel")
        self.leave_channel_id = data.get("leave_channel", self.welcome_channel_id)
        self.welcome_message = self.convert_dict(data.get("welcome_message"))
        self.welcome_DMmessage = self.convert_dict(data.get("welcome_DMmessage"))
        self.leave_message = self.convert_dict(data.get("leave_message", self.welcome_message))

    @property
    def welcome_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.welcome_channel_id)

    @property
    def leave_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.leave_channel_id)
