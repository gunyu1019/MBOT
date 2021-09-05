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
along with PUBG BOT.  If not, see <https://www.gnu.org/licenses/>.
"""

import ast
import asyncio
import datetime
import platform
import traceback

import discord
from discord.ext import commands

from config.config import parser
from module import commands as _command
from module.message import MessageSendable
from utils.database import get_database
from utils.perm import check_perm
from utils.prefix import get_prefix


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @_command.command(aliases=["디버그"], permission=1, interaction=False)
    async def debug(self, ctx):
        list_message = ctx.options
        if len(list_message) < 1:
            embed = discord.Embed(title="Metarix 도우미", description='사용하실 커맨드를 작성해주세요.', color=self.color)
            await ctx.send(embed=embed)
            return
        cmd = " ".join(list_message[0:])
        if cmd.startswith("```") and cmd.endswith("```"):
            cmd = cmd[3:-3]
            if cmd.startswith("py"):
                cmd = cmd[2:]
        before_cmd = cmd
        time1 = datetime.datetime.now()

        embed = discord.Embed(title="Debugging", color=self.color)
        embed.add_field(name="입력", value=f"```py\n{before_cmd}\n```", inline=False)
        embed.add_field(name="출력", value="```py\nevaling...\n```", inline=False)
        embed.add_field(name="출력(Type)", value="```py\nevaling...\n```", inline=False)
        embed.add_field(name="소요시간", value="```\ncounting...\n```", inline=False)
        msg = await ctx.send(embed=embed)
        try:
            fn_name = "__eval"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                "self": self,
                "bot": self.client,
                "discord": discord,
                "ctx": ctx,
                "commands": commands,
                "channel": ctx.channel,
                "author": ctx.author,
                "server": ctx.guild,
                "__import__": __import__,
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = await eval(f"{fn_name}()", env)
            time2 = datetime.datetime.now()
            microsecond = (round(float(f"0.{(time2 - time1).microseconds}"), 3))
            second = (time2 - time1).seconds
            try:
                embed.set_field_at(1, name="출력", value=f"```py\n{result}\n```", inline=False)
                embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(result)}\n```", inline=False)
                embed.set_field_at(3, name="소요시간", value=f"```\n{second + microsecond}초\n```", inline=False)
                await msg.edit(embed=embed)
            except discord.errors.HTTPException:
                with open("debug_result.txt", "w") as f:
                    f.write(f"debug : \n{cmd}\n-----\n{result}")
                embed.set_field_at(1, name="출력",
                                   value="```length of result is over 1000. here is text file of result```",
                                   inline=False)
                embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(result)}\n```", inline=False)
                embed.set_field_at(3, name="소요시간", value=f"```\n{second + microsecond}초\n```", inline=False)
                await msg.edit(embed=embed)
                await ctx.send(file=discord.File("eval_result.txt"))
        except Exception as e:
            embed.set_field_at(1, name="출력", value=f"```pytb\n{traceback.format_exc()}\n```", inline=False)
            embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(e)}\n```", inline=False)
            embed.set_field_at(3, name="소요시간", value=f"```\n동작 중단\n```", inline=False)
            await msg.edit(embed=embed)
        return

    @_command.command(permission=1, interaction=False)
    async def cmd(self, ctx):
        list_message = ctx.options
        prefix = get_prefix(self.client, ctx)[0]
        if len(list_message) < 1:
            embed = discord.Embed(title="Metarix 도우미", description=prefix + "cmd <명령어>\n명령어를 입력해주세요!", color=self.color)
            await ctx.send(embed=embed)
            return
        search = " ".join(list_message[0:])
        proc = await asyncio.create_subprocess_shell(search,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        if platform.system() == "Windows":
            decode = 'cp949'
        else:
            decode = 'UTF-8'
        stdout, stderr = await proc.communicate()
        if stderr.decode(decode) == "":
            embed = discord.Embed(title="cmd", description=stdout.decode(decode), color=self.color)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="에러!", description=stderr.decode(decode), color=self.color)
            await ctx.send(embed=embed)
        return

    @_command.command(name="블랙리스트", permission=9, interaction=False)
    async def blacklist(self, ctx):
        list_message = ctx.options
        prefix = get_prefix(self.client, ctx)[0]
        if len(list_message) < 1:
            embed = discord.Embed(title="Metarix 도우미", description=f"{prefix}블랙리스트 <등록/제거/여부> <맨션(선택)> 와 같이 작성해주세요.",
                                  color=self.color)
            await ctx.send(embed=embed)
            return
        mod = list_message[0]
        if mod == "여부":
            if len(list_message) > 1:
                mention = int(list_message[1].replace("<@", "").replace(">", "").replace("!", ""))
                member = await ctx.guild.fetch_member(mention)
                if member is None:
                    embed = discord.Embed(title="PUBG BOT 도우미",
                                          description=f"올바른 유저를 기재하여 주세요.",
                                          color=self.color)
                    await ctx.send(embed=embed)
                    return
            else:
                member = ctx.author
            result = check_perm(member)
            if 4 >= result:
                embed = discord.Embed(title="Blacklist!", description="이 사람은 블랙리스트에 등재되어 있지 않습니다.", color=self.color)
            else:
                embed = discord.Embed(title="Blacklist!", description="이 사람은 블랙리스트에 등재되어 있습니다.", color=self.color)
            await ctx.send(embed=embed)
            return
        elif mod == "등록":
            if len(list_message) < 2:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"블랙리스트에 등재할 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            mention = int(list_message[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await ctx.guild.fetch_member(mention)
            if member is None:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"올바른 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            if 2 < check_perm(ctx.author):
                embed = discord.Embed(title="에러", description="권한이 부족합니다.", color=0xaa0000)
                await ctx.send(embed=embed)
                return
            if 2 >= check_perm(member):
                embed = discord.Embed(
                    title="Blacklist!",
                    description="봇 관리자의 권한을 가지고 있는 사용자는 블랙리스트에 등재할 수 없습니다.",
                    color=self.color
                )
                await ctx.send(embed=embed)
                return
            connect = get_database()
            cur = connect.cursor()
            sql_black = "insert into blacklist(id) value(%s)"
            if 9 == check_perm(member):
                embed = discord.Embed(title="Blacklist!", description=f"{member}는 이미 등재되어 있습니다.",
                                      color=self.color)
                await ctx.send(embed=embed)
                connect.commit()
                connect.close()
                return
            cur.execute(sql_black, mention)
            connect.commit()
            connect.close()
            embed = discord.Embed(title="Blacklist!", description=f"{member}가 블랙리스트에 추가되었습니다!", color=self.color)
            await ctx.send(embed=embed)
            return
        elif mod == "제거":
            if len(list_message) < 2:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"블랙리스트에 등재할 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            mention = int(list_message[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await ctx.guild.fetch_member(mention)
            if 2 < check_perm(ctx.author):
                embed = discord.Embed(title="에러", description="권한이 부족합니다.", color=0xaa0000)
                await ctx.send(embed=embed)
                return
            if member is None:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"올바른 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            connect = get_database()
            cur = connect.cursor()
            sql_delete = "delete from blacklist where id=%s"
            if 4 >= check_perm(member):
                embed = discord.Embed(title="Blacklist!", description=f"{member}는, 블랙리스트에 추가되어 있지 않습니다.",
                                      color=self.color)
                await ctx.send(embed=embed)
                connect.commit()
                connect.close()
                return
            cur.execute(sql_delete, mention)
            connect.commit()
            connect.close()
            embed = discord.Embed(title="Blacklist!", description=f"{member}가 블랙리스트에서 제거되었습니다!", color=self.color)
            await ctx.send(embed=embed)
            return


def setup(client):
    return Command(client)
