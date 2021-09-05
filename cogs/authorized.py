import json
import logging
import os

import discord
from enum import Enum
from datetime import datetime, timedelta
from pytz import timezone
from discord.ext import commands

from config.config import parser
from module.components import ActionRow, Button
from module.interaction import ComponentsContext, InteractionContext
from module.message import MessageSendable
from utils.convert import Convert
from utils.database import Database
from utils.directory import directory
from utils.models import Authorized

logger = logging.getLogger(__name__)
DBS = None


class RobotCheckType(Enum):
    image = 0
    sound = 1


class AuthorizedReceived(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(os.path.join(directory, "data", "ticket.json"), "r", encoding='utf-8') as file:
            self.ticket = json.load(fp=file)
        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.robot_process = discord.Embed(
            title="인증(Authorized)",
            description="이 서버({guild})에 접근하기 위해서는 캡차 과정을 통과하셔야 합니다. 아래의 {tp}의 값을 알맞게 입력해주세요.",
            color=self.color
        )
        self.robot_failed = discord.Embed(
            title="실패",
            description="인증에 실패하였습니다. 인증을 다시 시도해주시기 바랍니다.",
            color=self.color
        )
        self.robot_timeout1 = discord.Embed(
            title="실패",
            description="인증 시간(5분)이 초과되어 인증에 실패하였습니다. 인증을 다시 시도해주시기 바랍니다.",
            color=self.warning_color
        )
        self.robot_timeout2 = discord.Embed(
            title="실패",
            description="인증 입력 시간(10초)가 초과되어 인증에 실패하였습니다. 인증을 다시 시도해주시기 바랍니다.",
            color=self.warning_color
        )
        self.robot_process.set_footer(text="Powered by Naver Captcha")

    async def robot_check(self, member: discord.Member, mode: RobotCheckType) -> bool:
        mode_commnet = {
            0: "이미지",
            1: "음성"
        }
        self.robot_process.description = self.robot_process.description.format(
            guild=member.guild, tp=mode_commnet[mode.value]
        )

        try:
            channel = member.dm_channel
            if channel is None:
                channel = await member.create_dm()
            _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)

            await _channel.send(
                embed=self.robot_process,
                components=[
                    ActionRow(components=[
                        Button(style=1, custom_id="authorized", label="인증하기"),
                        Button(
                            style=1,
                            custom_id="change_mode",
                            label="유형 변경({0}->{1})".format(
                                mode_commnet[mode.value], mode_commnet[1 - mode.value]
                            )
                        )
                    ])
                ]
            )
        except discord.Forbidden:
            return False
        return True

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        database = Database(bot=self.bot, guild=member.guild)
        if not database.get_activation("authorized"):
            return
        data = database.get_data("authorized")
        if data.reaction:
            return

        if data.robot:
            await self.robot_check(mode=RobotCheckType.image)
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        database = Database(bot=self.bot, guild=member.guild)
        if not database.get_activation("authorized"):
            return
        data = database.get_data("authorized")
        if datetime.now(tz=timezone("UTC")) - member.joined_at < timedelta(seconds=data.in_out_count):
            await member.ban(reason="AUTO BAN: Detection of an act of In and Out")
        return


def setup(client):
    client.add_cog(AuthorizedReceived(client))
