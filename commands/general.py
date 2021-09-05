"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import json
import discord

from config.config import parser
from module import commands
from utils.prefix import get_prefix, set_prefix

default_prefixes = list(json.loads(parser.get("DEFAULT", "default_prefixes")))


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @commands.command(aliases=['핑'], permission=4)
    async def ping(self, ctx):
        now = datetime.datetime.utcnow()
        if now > ctx.created_at:
            response_ping_r = now - ctx.created_at
        else:
            response_ping_r = ctx.created_at - now
        response_ping_read = float(str(response_ping_r.seconds) + "." + str(response_ping_r.microseconds))
        first_latency = round(self.client.latency * 1000, 2)
        embed = discord.Embed(
            title="Pong!",
            description=f"클라이언트 핑상태: {first_latency}ms\n응답속도(읽기): {round(response_ping_read * 1000, 2)}ms",
            color=self.color)
        msg = await ctx.send(embed=embed)
        now = datetime.datetime.utcnow()
        if now > msg.created_at:
            response_ping_w = now - msg.created_at
        else:
            response_ping_w = msg.created_at - now
        response_ping_write = float(str(response_ping_w.seconds) + "." + str(response_ping_w.microseconds))
        embed = discord.Embed(
            title="Pong!",
            description=f"클라이언트 핑상태: {first_latency}ms\n응답속도(읽기/쓰기): {round(response_ping_read * 1000, 2)}ms/{round(response_ping_write * 1000, 2)}ms",
            color=self.color)
        await msg.edit(embed=embed)
        return

    @commands.command(aliases=['접두어'], interaction=False, permission=4)
    async def prefix(self, ctx):
        list_message = ctx.options
        prefix = get_prefix(bot=self.client, ctx=ctx)[0]

        def help_message(msg: str = ""):
            return f"{prefix}접두어 <설정|초기화|정보> <접두어(옵션)>: {msg}\n접두어 설정은 \\n,\\t,(공백) 사용금지, 20자 미만으로 설정이 가능합니다."

        if ctx.guild:
            if len(list_message) < 1:
                embed = discord.Embed(
                    title="에러",
                    description=help_message("설정/초기화/정보 중 한가지를 선택해주세요."),
                    color=self.color)
                await ctx.send(embed=embed)
                return
            mode = list_message[0]
            if mode == "정보":
                embed = discord.Embed(
                    title="접두어",
                    description=f"{ctx.guild.name}서버의 접두어는 {prefix}(명령어)입니다.",
                    color=self.color)
                await ctx.send(embed=embed)
            elif mode == "초기화":
                set_prefix(self.client, ctx.guild, default_prefixes[0])
                embed = discord.Embed(title="접두어", description="성공적으로 접두어를 초기화 하였습니다.", color=self.color)
                await ctx.send(embed=embed)
            elif mode == "설정":
                if len(list_message) < 2:
                    embed = discord.Embed(title="에러", description=help_message("변경하실 접두어를 작성해주세요."), color=self.color)
                    await ctx.send(embed=embed)
                    return
                new_prefix = list_message[1]
                if len(list_message) > 3 or new_prefix.find("\n") != -1 or new_prefix.find("\t") != -1:
                    embed = discord.Embed(title="에러", description=help_message("금칙어가 포함되어 있습니다."), color=self.color)
                    await ctx.send(embed=embed)
                    return
                elif len(new_prefix) > 20:
                    embed = discord.Embed(title="에러", description=help_message("20자 이내로 설정해주세요."), color=self.color)
                    await ctx.send(embed=embed)
                    return
                set_prefix(self.client, ctx.guild, new_prefix)
                embed = discord.Embed(title="접두어", description=f"성공적으로 접두어를 {new_prefix}로 설정 하였습니다.", color=self.color)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="에러",
                    description=help_message("설정/초기화/정보 중 한가지를 선택해주세요."),
                    color=self.color)
                await ctx.send(embed=embed)
                return
        else:
            embed = discord.Embed(title="에러", description="접두어 기능은 서버에서만 사용 가능합니다.", color=self.color)
            await ctx.send(embed=embed)

    @commands.command(name="정보", permission=4)
    async def information(self, ctx):
        total = 0
        for i in self.client.guilds:
            total += i.member_count
        embed = discord.Embed(title='Metarix', color=self.color)
        embed.add_field(
            name='개발',
            value='[건유1019#0001](https://yhs.kr/YBOT/forum.html)',
            inline=True
        )
        embed.add_field(
            name='서버수 / 유저수',
            value=f'{len(self.client.guilds)}서버/{total}명',
            inline=True
        )
        embed.add_field(
            name='Metarix 버전',
            value=f'{parser.get("DEFAULT","version")}',
            inline=True
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)
        return


def setup(client):
    return Command(client)
