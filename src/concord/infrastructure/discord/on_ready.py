import logging
from datetime import datetime, timedelta, timezone

import discord
from discord import ClientUser
from discord.ext.commands import Bot, Cog

JST = timezone(timedelta(hours=+9), "JST")


class OnReady(Cog):
    """OnReady"""

    def __init__(self, *, bot: Bot, logger: logging.Logger) -> None:
        self._logger = logger
        self._bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        """on_ready

        Discordとの接続が完了した際に呼び出される。

        """
        await self.__print_status(user=self._bot.user)

    async def __print_status(self, user: ClientUser | None) -> None:
        msg = "--------------------------------------"
        msg += " LOG IN STATUS"
        if user is not None:
            msg += f"\tUser name: {user.name}"
            msg += f"\tUser id  : {user.id}"
        msg += f"\tTime     : {datetime.now(JST).strftime('%Y/%m/%d %H:%M:%S')}"
        msg += f"\tDiscord  {discord.__version__}"
        msg += "--------------------------------------"
        self._logger.info(msg)
