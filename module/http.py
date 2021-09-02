"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
from discord.http import Route


class SlashRoute(Route):
    BASE = "https://discord.com/api/v9"


class InteractionData:
    def __init__(self, interaction_token, interaction_id=None, application_id=None):
        self.id = str(interaction_id)
        self.application = str(application_id)
        self.token: str = interaction_token


class HttpClient:
    def __init__(self, http: discord.http.HTTPClient):
        self.http = http

    async def post_defer_response(self, payload: dict, interaction: InteractionData):
        r = SlashRoute("POST", "/interactions/{id}/{token}/callback", id=interaction.id, token=interaction.token)
        await self.http.request(r, json=payload)

    async def post_initial_response(self, payload: dict, interaction: InteractionData):
        r = SlashRoute("POST", "/interactions/{id}/{token}/callback", id=interaction.id, token=interaction.token)
        data = {"type": 4, "data": payload}
        return await self.http.request(r, json=data)

    async def post_initial_components_response(self, payload: dict, interaction: InteractionData):
        r = SlashRoute("POST", "/interactions/{id}/{token}/callback", id=interaction.id, token=interaction.token)
        data = {"type": 7, "data": payload}
        return await self.http.request(r, json=data)

    async def get_initial_response(self, interaction: InteractionData):
        r = SlashRoute(
            "GET", "/webhooks/{id}/{token}/messages/@original",
            id=interaction.application, token=interaction.token
        )
        return await self.http.request(r)

    async def edit_initial_response(self, interaction: InteractionData, payload: dict = None, form=None, files=None):
        if files is not None or form is not None:
            return await self.edit_followup("@original", form=form, files=files, interaction=interaction)
        return await self.edit_followup("@original", payload=payload, interaction=interaction)

    async def delete_initial_response(self, interaction: InteractionData):
        await self.delete_followup("@original", interaction=interaction)

    async def post_followup(self, interaction: InteractionData, payload: dict = None, form=None, files=None):
        r = SlashRoute("POST", "/webhooks/{id}/{token}", id=interaction.application, token=interaction.token)
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_followup(
            self, message_id, interaction: InteractionData,
            payload: dict = None, form=None, files=None
    ):
        r = SlashRoute(
            "PATCH", "/webhooks/{id}/{token}/messages/{message_id}",
            id=interaction.application, token=interaction.token, message_id=message_id
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def delete_followup(self, message_id, interaction: InteractionData):
        r = SlashRoute(
            "DELETE", "/webhooks/{id}/{token}/messages/{message_id}",
            id=interaction.application, token=interaction.token, message_id=message_id
        )
        await self.http.request(r)

    async def create_message(self, channel_id, payload: dict = None, form=None, files=None):
        r = SlashRoute('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_message(self, channel_id, message_id, payload: dict = None, form=None, files=None):
        r = SlashRoute(
            'PATCH', '/channels/{channel_id}/messages/{message_id}',
            channel_id=channel_id, message_id=message_id
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def create_thread_with_message(self, channel_id, message_id, payload: dict):
        r = SlashRoute(
            'POST', '/channels/{channel_id}/messages/{message_id}/threads',
            channel_id=channel_id, message_id=message_id
        )
        return await self.http.request(r, json=payload)

    async def create_thread_without_message(self, channel_id, payload: dict):
        r = SlashRoute('POST', '/channels/{channel_id}/threads', channel_id=channel_id)
        return await self.http.request(r, json=payload)

    async def edit_channel(self, channel_id, payload: dict):
        r = SlashRoute('PATCH', '/channels/{channel_id}', channel_id=channel_id)
        return await self.http.request(r, json=payload)

    async def delete_channel(self, channel_id):
        r = SlashRoute('DELETE', '/channels/{channel_id}', channel_id=channel_id)
        return await self.http.request(r)

    async def join_thread(self, channel_id):
        return await self.add_user_to_thread(channel_id=channel_id, user_id="@me")

    async def add_user_to_thread(self, channel_id, user_id):
        r = SlashRoute(
            'PUT', '/channels/{channel_id}/thread-members/{user_id}',
            channel_id=channel_id, user_id=user_id
        )
        return await self.http.request(r)

    async def leave_thread(self, channel_id):
        return await self.remove_user_from_thread(channel_id=channel_id, user_id="@me")

    async def remove_user_from_thread(self, channel_id, user_id):
        r = SlashRoute(
            'DELETE', '/channels/{channel_id}/thread-members/{user_id}',
            channel_id=channel_id, user_id=user_id
        )
        return await self.http.request(r)

    async def get_gateway(self, *, encoding='json', v=6, zlib=True):
        try:
            data = await self.http.request(SlashRoute('GET', '/gateway'))
        except discord.HTTPException as exc:
            raise discord.GatewayNotFound() from exc
        if zlib:
            value = '{0}?encoding={1}&v={2}&compress=zlib-stream'
        else:
            value = '{0}?encoding={1}&v={2}'
        return value.format(data['url'], encoding, v)

    async def get_bot_gateway(self, *, encoding='json', v=6, zlib=True):
        try:
            data = await self.http.request(SlashRoute('GET', '/gateway/bot'))
        except discord.HTTPException as exc:
            raise discord.GatewayNotFound() from exc

        if zlib:
            value = '{0}?encoding={1}&v={2}&compress=zlib-stream'
        else:
            value = '{0}?encoding={1}&v={2}'
        return data['shards'], value.format(data['url'], encoding, v)
