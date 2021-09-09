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


class Logging(DatabaseModel):
    def __init__(self, data: dict, bot: discord.Client):
        super().__init__(data, bot)
        self.data = data
        self.bot = bot

        self.message_log_channel_id = data.get("message_log_id")
        self.warning_log_channel_id = data.get("warning_log_id", self.message_log_channel_id)
        self.channel_log_channel_id = data.get("channel_log_id", self.message_log_channel_id)
        self.voice_log_channel_id = data.get("voice_log_id", self.message_log_channel_id)
        self.guild_log_channel_id = data.get("guild_log_id", self.message_log_channel_id)
        self.member_log_channel_id = data.get("member_log_id", self.message_log_channel_id)

    @property
    def warning_log_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.warning_log_channel_id) or self.message_log_channel

    @property
    def channel_log_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.channel_log_channel_id) or self.message_log_channel

    @property
    def message_log_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.message_log_channel_id)

    @property
    def voice_log_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.voice_log_channel_id) or self.message_log_channel

    @property
    def guild_log_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.guild_log_channel_id) or self.message_log_channel

    @property
    def member_log_channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.member_log_channel_id) or self.message_log_channel

    def __getattr__(self, item):
        return bool(self.data.get(item))


class DatabaseMessage(DatabaseModel):
    def __init__(self, bot: discord.Client, data: dict, guild=None):
        super().__init__(data=data, bot=bot)
        self._guild = guild
        self.bot = bot
        self.data = data

        self.id = data['id']
        self.channel_id = data['channel_id']
        self.guild_id = data.get('guild_id')
        self.webhook_id = data.get('webhook_id')

        self.content = data.get("content")

        self.author_id = data.get("author_id")
        self.author_name = data.get("author_name")
        self.author_tag = data.get("author_tag")
        self.author_avatar = data.get("author_avatar")
        self.author_bot = data.get("bot")

        self.pinned = data.get("pin", False)

        self.created_at = data["timestamp"]
        self.edited_at = data.get("edited_timestamp")

    @property
    def channel(self) -> discord.TextChannel:
        return self.guild.get_channel(self.channel_id) or self.guild.get_thread(self.channel_id)

    @property
    def embeds(self):
        return [discord.Embed.from_dict(embed) for embed in self.convert_dict(self.data.get("embeds", "[]"))]

    @property
    def attachments(self):
        return self.convert_dict(self.data.get("attachment", "[]"))

    @property
    def author(self):
        return self.guild.get_member(self.author_id) or self.bot.get_user(self.author_id)

    @property
    def guild(self) -> discord.Guild:
        return self._guild or self.bot.get_guild(self.guild_id)

    @property
    def stickers(self):
        return [DatabaseSticker({
            "type": self.convert_dict(self.data.get("stickers_type"))[index],
            "name": value.get("name"),
            "url": value.get("url"),
            "id": value.get("id")
        }) for index, value in enumerate(self.convert_dict(self.data.get("stickers")))
        ]


class DatabaseSticker:
    def __init__(self, data):
        self.name = data.get('name')
        self.id = data.get('id')
        self.url = data['url']
        self.type = data['type']
