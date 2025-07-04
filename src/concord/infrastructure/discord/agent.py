import logging
import pprint
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from discord import Intents
from discord.ext.commands import Bot, Cog

from concord.cli.arguments import on_launch
from concord.infrastructure.config.from_files import ConfigArgs
from concord.infrastructure.discord.dynamic_import import import_classes_from_directory
from concord.infrastructure.logging.logger_factory import get_logger
from concord.infrastructure.logging.logger_notifier import DiscordLogHandler

from .cached_channels import CachedChannels
from .on_connecting import OnConnecting
from .on_ready import OnReady

if TYPE_CHECKING:
    from concord.model.import_class import LoadedClass


class Agent:
    """BOTのインスタンスを管理するクラス

    Notes:
        CLIでの実行時に以下を引数に与えることを想定している

        - bot_name (str): BOTの名前
        - tool_directory_path (Path, optional): ツールのディレクトリパス
        - is_debug (bool, optional): デバッグモードかどうか
    """

    def __init__(self, utils_dirpath: Path | None = None) -> None:
        log_dirpath = utils_dirpath / "logs" if utils_dirpath is not None else None
        config_dirpath = utils_dirpath / "configs" if utils_dirpath is not None else None
        args = on_launch()
        log_level = logging.DEBUG if args.is_debug else logging.INFO
        self.logger = get_logger(
            name=args.bot_name,
            level=log_level,
            log_dir=log_dirpath,
        )
        self._tool_directory_paths = args.tool_directory_paths
        self.config = ConfigArgs(
            bot_name=args.bot_name,
            logger=self.logger,
            config_dir=config_dirpath,
        )
        self.bot = Bot(
            intents=Intents.all(),
            command_prefix=("/"),
            description=self.config.bot.description,
            # help_command=None,
        )
        self.cached_channels = CachedChannels(
            bot=self.bot,
            config=self.config,
            logger=self.logger,
        )
        self.bot.event(self.on_ready)

    async def greetings(self) -> str:
        """グリーティングメッセージを返す"""
        user = self.bot.user
        if user is None:
            msg = "User is None"
            self.logger.error(msg)
            raise ValueError(msg)
        msg = f"Logged in as {user.name} ({user.id})"
        msg += f"Guilds: {len(self.bot.guilds)}"
        msg += f"Channels: {len(list(self.bot.get_all_channels()))}"
        return msg

    async def on_ready(self) -> None:
        """on_readyのオーバーライド

        - デフォルトコグの追加
        - extensionの読み込み
        - ログイン確認
        - ログチャンネルへのログ送信
        """
        self.logger.info("function `on_ready` called")

        # Add: cog
        await self.bot.add_cog(OnConnecting(logger=self.logger))
        await self.bot.add_cog(OnReady(bot=self.bot, logger=self.logger))
        self.logger.info("add cog `OnConnecting` and `OnReady`")

        # Load: extension
        loaded_extensions: list[str] = []
        for tool_directory_path in self._tool_directory_paths:
            tools: list[LoadedClass[type[Cog]]] = import_classes_from_directory(
                directory_path=tool_directory_path.as_posix(),
                base_class=Cog,
                include_name=["__tool__.py"],
                logger=self.logger,
            )
            for tool in tools:
                try:
                    await self.bot.add_cog(tool.class_type(agent=self))
                    loaded_extensions.append(tool.class_type.__name__)
                except Exception:
                    msg = f"failed to load extension : {tool.name}\n{traceback.format_exc()}"
                    self.logger.exception(msg)
                    raise

        msg = f"load extension from `tool_directory_paths`: {loaded_extensions}"
        self.logger.info(msg)

        # Log: ログイン確認
        msg = await self.greetings()
        self.logger.info(msg)

        # Log: ログチャンネルへのログ送信 (ログイン後から送信可能になる)
        self.logger.addHandler(DiscordLogHandler(self.cached_channels.log_channel))
        self.logger.info("Enabled logging to discord")

        # Check: Post message
        await self.cached_channels.dev_channel.send("Good morning, Master.\nGood work today.")
        if len(loaded_extensions) > 0:
            await self.cached_channels.dev_channel.send(
                f"Available commands:\n{
                    pprint.pformat(
                        loaded_extensions,
                        indent=2,
                    )
                }",
            )
        else:
            await self.cached_channels.dev_channel.send("No commands available")
        msg = "Sent message to dev channel"
        self.logger.info(msg)

    async def run(self) -> None:
        """BOTを起動する

        Args:
            None

        Returns:
            None
        """
        await self.bot.start(self.config.bot.discord_token)
