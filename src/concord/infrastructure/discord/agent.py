import logging
import pprint

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


class Agent:
    """BOTのインスタンスを管理するクラス

    Notes:
        CLIでの実行時に以下を引数に与えることを想定している

        - bot_name (str): BOTの名前
        - tool_directory_path (Path, optional): ツールのディレクトリパス
        - is_debug (bool, optional): デバッグモードかどうか
    """

    def __init__(self) -> None:
        args = on_launch()
        log_level = logging.DEBUG if args.is_debug else logging.INFO
        self._logger = get_logger(name=args.bot_name, level=log_level)
        self._tool_directory_paths = args.tool_directory_paths
        self._config = ConfigArgs(bot_name=args.bot_name, logger=self._logger)
        self._bot = Bot(
            intents=Intents.all(),
            command_prefix=("/"),
            description=self._config.bot.description,
            # help_command=None,
        )
        self._cached_channels = CachedChannels(
            bot=self._bot,
            config=self._config,
            logger=self._logger,
        )
        self._bot.event(self.on_ready)

    async def greetings(self) -> str:
        """グリーティングメッセージを返す"""
        user = self._bot.user
        if user is None:
            msg = "User is None"
            self._logger.error(msg)
            raise ValueError(msg)
        msg = f"Logged in as {user.name} ({user.id})"
        msg += f"Guilds: {len(self._bot.guilds)}"
        msg += f"Channels: {len(list(self._bot.get_all_channels()))}"
        return msg

    async def on_ready(self) -> None:
        """on_readyのオーバーライド

        - デフォルトコグの追加
        - extensionの読み込み
        - ログイン確認
        - ログチャンネルへのログ送信
        """
        self._logger.info("function `on_ready` called")

        # Add: cog
        await self._bot.add_cog(OnConnecting(logger=self._logger))
        await self._bot.add_cog(OnReady(bot=self._bot, logger=self._logger))
        self._logger.info("add cog `OnConnecting` and `OnReady`")

        # Load: extension
        loaded_extensions: list[str] = []
        for tool_directory_path in self._tool_directory_paths:
            for tool in import_classes_from_directory(
                directory_path=tool_directory_path.as_posix(),
                base_class=type(Cog),
                include_name=["__tool__.py"],
                logger=self._logger,
            ):
                await self._bot.load_extension(tool.name)
                loaded_extensions.append(tool.class_obj.__name__)
        msg = f"load extension from `tool_directory_paths`: {loaded_extensions}"
        self._logger.info(msg)

        # Log: ログイン確認
        msg = await self.greetings()
        self._logger.info(msg)

        # Log: ログチャンネルへのログ送信 (ログイン後から送信可能になる)
        self._logger.addHandler(DiscordLogHandler(self._cached_channels.log_channel))
        self._logger.info("Enabled logging to discord")

        # Check: Post message
        await self._cached_channels.dev_channel.send("Good morning, Master.\nGood work today.")
        if len(loaded_extensions) > 0:
            await self._cached_channels.dev_channel.send(
                f"Available commands:\n{
                    pprint.pformat(
                        loaded_extensions,
                        indent=2,
                    )
                }",
            )
        else:
            await self._cached_channels.dev_channel.send("No commands available")
        msg = "Sent message to dev channel"
        self._logger.info(msg)

    async def run(self) -> None:
        """BOTを起動する

        Args:
            None

        Returns:
            None
        """
        await self._bot.start(self._config.bot.discord_token)
