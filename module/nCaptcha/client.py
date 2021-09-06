import aiohttp
import asyncio

from .https import HttpClient


class Client:
    def __init__(
            self,
            id: str, secret: str,
            session: aiohttp.ClientSession = None,
            loop: asyncio.AbstractEventLoop = None
    ):
        self.id = id
        self.secret = secret
        self.http = HttpClient(
            id=self.id,
            secret=self.secret,
            loop=loop,
            session=session
        )

        self.last_key = None
        self.type = None

    async def get_image(self):
        self.type = 0
        code_result = await self.http.image_key(code=0)
        self.last_key = code_result.get("key")
        return await self.http.image_get(key=self.last_key)

    async def refresh_image(self, key: str = None):
        if key is None:
            key = self.last_key
        return await self.http.image_get(key=key)

    async def get_sound(self):
        self.type = 1
        code_result = await self.http.sound_key(code=0)
        self.last_key = code_result.get("key")
        return await self.http.sound_get(key=self.last_key)

    async def refresh_sound(self, key: str = None):
        if key is None:
            key = self.last_key
        return await self.http.sound_get(key=key)

    async def verification(self, key: str, value: str, type: int = None):
        if type is None:
            type = self.type

        if type == 0:
            return await self.http.image_key(code=1, key=key, value=value)
        elif type == 1:
            return await self.http.sound_key(code=1, key=key, value=value)
