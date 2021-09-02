import os

import discord
from discord.ext import commands

from config.config import parser
from config.log_config import log

from module.http import HttpClient
from utils.prefix import get_prefix
from utils.token import token


# async def launch_shards():
#     http = HttpClient(http=bot.http)
#     if bot.shard_count is None:
#         bot.shard_count, gateway = await http.get_bot_gateway(v=9)
#     else:
#         gateway = await http.get_gateway(v=9)
#
#     getattr(bot, "_connection").shard_count = bot.shard_count
#
#     shard_ids = bot.shard_ids or range(bot.shard_count)
#     getattr(bot, "_connection").shard_ids = shard_ids
#
#     for shard_id in shard_ids:
#         initial = shard_id == shard_ids[0]
#         await bot.launch_shard(gateway, shard_id, initial=initial)
#
#     getattr(bot, "_connection").shards_launched.set()

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

    log.info("Metarix을 불러오는 중입니다.")
    if parser.getboolean("DEFAULT", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = commands.AutoShardedBot(
            command_prefix=get_prefix,
            intents=discord.Intents.all(),
            enable_debug_events=True
        )
    else:
        bot = commands.Bot(
            command_prefix=get_prefix,
            intents=discord.Intents.all(),
            enable_debug_events=True
        )

    bot.remove_command("help")
    cogs = ["cogs." + file[:-3] for file in os.listdir(f"{directory}/cogs") if file.endswith(".py")]
    for cog in cogs:
        bot.load_extension(cog)

    bot.run(token)
