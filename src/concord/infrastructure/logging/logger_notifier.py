import asyncio
import logging
import queue
import threading

from discord.channel import TextChannel
from discord.errors import Forbidden, HTTPException, NotFound
from discord.threads import Thread
from pyresults import Err, Ok, Result

from concord.exception.send_log import DiscordSendLogError

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (module: %(module)s, func: %(funcName)s)"

log_queue: queue.Queue[tuple[str, TextChannel | Thread]] = queue.Queue()


class DiscordLogHandler(logging.Handler):
    def __init__(self, log_channel: TextChannel | Thread) -> None:
        super().__init__(level=logging.INFO)
        self.log_channel = log_channel
        self.setFormatter(
            logging.Formatter(
                FORMAT,
            ),
        )

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        log_queue.put((log_entry, self.log_channel))


class AsyncDispatcher:
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop)
        self.thread.start()

    def start_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.worker())

    async def worker(self) -> None:
        while True:
            log_entry, channel = await self.loop.run_in_executor(None, log_queue.get)
            result = await self.send_log(log_entry, channel)
            if result.is_err():
                raise DiscordSendLogError(result.unwrap_err())

    async def send_log(self, log_entry: str, channel: TextChannel | Thread) -> Result[None, str]:
        try:
            await channel.send(content=f"```bash\n{log_entry}\n```")
            return Ok(None)
        except (HTTPException, Forbidden, NotFound, ValueError, TypeError) as e:
            return Err(f"{e!s}")
