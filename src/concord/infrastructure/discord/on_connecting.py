import logging

from discord.ext.commands import Cog


class OnConnecting(Cog):
    def __init__(self, *, logger: logging.Logger) -> None:
        self._logger = logger

    @Cog.listener()
    async def on_connect(self) -> None:
        self._logger.info("Connecting to Discord")
