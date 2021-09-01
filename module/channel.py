import discord
from discord.state import ConnectionState
from enum import Enum
from typing import Optional

from module.http import HttpClient
from module.errors import InvalidArgument
from module.message import Message, MessageSendable


class ThreadType(Enum):
    NEWS = 10
    PUBLIC = 11
    PRIVATE = 12


class ChannelType(discord.ChannelType):
    thread_news = ThreadType.NEWS
    thread_public = ThreadType.PUBLIC
    thread_private = ThreadType.PRIVATE


class TextChannel(MessageSendable):
    def __init__(self, state: ConnectionState, channel: discord.TextChannel):
        self._state = state
        self.http = HttpClient(http=self._state.http)
        self.channel = channel

        super().__init__(
            state=self._state,
            channel=channel
        )

        self.guild = self.channel.guild

    async def create_thread(
            self,
            name, *,
            message: Message = None,
            duration: int = 1440,
            type: ThreadType = ThreadType.PUBLIC,
            invitable: bool = False
    ):
        if invitable and type != ThreadType.PRIVATE:
            raise InvalidArgument("invitable can only PRIVATE THREAD CHANNEL")

        if message and (type or invitable):
            raise InvalidArgument("Create Thread With Message can only input duration and name")

        payload = {
            "name": name,
            "auto_archive_duration": duration
        }
        if message is None and type is not None:
            payload['type'] = type.value if isinstance(type, ThreadType) else type
        if type == ThreadType.PRIVATE and invitable:
            payload['invitable'] = invitable

        if message is not None:
            channel = await self.http.create_thread_with_message(
                message_id=message.id, channel_id=self.channel.id, payload=payload
            )
        else:
            channel = await self.http.create_thread_without_message(
                channel_id=self.channel.id, payload=payload
            )
        return Thread(guild=self.guild, state=self._state, data=channel)


class Thread(MessageSendable):
    def __init__(self, guild: discord.Guild, state: ConnectionState, data: dict):
        self.guild = guild
        self._state = state
        self.http = HttpClient(http=self._state.http)
        self._from_dict(data)
        super().__init__(state=self._state, channel=self)

    def _from_dict(self, data: dict):
        self.id = int(data['id'])
        self.parent_id = int(data['parent_id'])
        self.owner_id = int(data['owner_id'])
        self.type = get_enum(ChannelType, data['type'])

        self.last_message_id = getattr(discord.utils, "_get_as_snowflake")(data, 'last_message_id')
        self.slowmode_delay = data.get('rate_limit_per_user', 0)
        self.message_count = data['message_count']
        self.member_count = data['member_count']
        self._metadata(data['thread_metadata'])
        return

    def _metadata(self, data: dict):
        self.archived: bool = data.get("archived")
        self.archiver_id = getattr(discord.utils, "_get_as_snowflake")(data, 'archiver_id')
        self.auto_archive_duration: int = data.get('auto_archive_duration')
        self.archive_timestamp = discord.utils.parse_time(data.get('archive_timestamp'))
        self.locked = data.get('locked', False)

        self.invitable = data.get('invitable', True)

    @property
    def parent(self) -> Optional[discord.TextChannel]:
        return self.guild.get_channel(self.parent_id)

    @property
    def owner(self) -> Optional[discord.Member]:
        return self.guild.get_member(self.owner_id)

    @property
    def mention(self) -> str:
        return f'<#{self.id}>'

    @property
    def last_message(self) -> Optional[Message]:
        return getattr(self._state, "_get_message")(self.last_message_id) if self.last_message_id else None

    @property
    def category(self) -> Optional[discord.CategoryChannel]:
        parent = self.parent
        return parent.category

    @property
    def category_id(self) -> Optional[int]:
        parent = self.parent
        return parent.category_id

    async def edit(
            self,
            *,
            name: str = None,
            archived: bool = None,
            locked: bool = None,
            invitable: bool = None,
            slowmode_delay: int = None,
            auto_archive_duration: int = None,
    ):
        payload = {}

        if name is not None:
            payload['name'] = name
        if archived is not None:
            payload['archived'] = archived
        if locked is not None:
            payload['locked'] = locked
        if invitable is not None:
            payload['invitable'] = invitable
        if slowmode_delay is not None:
            payload['rate_limit_per_user'] = slowmode_delay
        if auto_archive_duration is not None:
            payload['auto_archive_duration'] = auto_archive_duration

        data = await self.http.edit_channel(self.id, **payload)
        return Thread(data=data, state=self._state, guild=self.guild)

    async def delete(self):
        await self.http.delete_channel(channel_id=self.id)
        return

    async def join(self):
        await self.http.join_thread(channel_id=self.id)
        return

    async def leave(self):
        await self.http.leave_thread(channel_id=self.id)
        return

    async def add_user(self, member: discord.Member):
        await self.http.add_user_to_thread(channel_id=self.id, user_id=member.id)
        return

    async def remove_user(self, member: discord.Member):
        await self.http.remove_user_from_thread(channel_id=self.id, user_id=member.id)
        return


def get_enum(cls, val):
    enum_val = [i for i in cls if i.value == val]
    if len(enum_val) == 0:
        return val
    return enum_val[0]