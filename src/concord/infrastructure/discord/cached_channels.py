import logging
from typing import Any

from discord import Thread
from discord.abc import GuildChannel
from discord.channel import TextChannel
from discord.ext.commands import Bot

from concord.infrastructure.config.from_files import ConfigArgs


class CachedChannels:
    """インスタンスをキャッシュするチャンネル

    Args:
        bot (Bot): Bot
        config (ConfigArgs): Config
        logger (logging.Logger): Logger

    Attributes:
        bot (Bot): Bot
        logger (logging.Logger): Logger
        channel_name2id (dict[str, int]): ChannelName to ChannelId
        channel_id2name (dict[int, str]): ChannelId to ChannelName
        dev_channel (TextChannel | Thread): Dev Channel
        log_channel (TextChannel | Thread): Log Channel
    """

    def __init__(self, *, bot: Bot, config: ConfigArgs, logger: logging.Logger) -> None:
        self.bot = bot
        self._logger = logger
        self._channel_name2id = config.bot.get_channel_to_id_mapping()
        self._channel_id2name = config.bot.get_id_to_channel_mapping()
        self._cached_channel_from_id: dict[int, TextChannel | Thread] = {}
        self._log_channel_id = config.bot.get_default_channel_id(name="log_channel")
        self._dev_channel_id = config.bot.get_default_channel_id(name="dev_channel")
        self._dev_channel: TextChannel | Thread | None = None
        self._log_channel: TextChannel | Thread | None = None

    @property
    def channel_name2id(self) -> dict[str, int]:
        return self._channel_name2id

    @channel_name2id.setter
    def channel_name2id(self, value: Any) -> None:  # noqa: ARG002, ANN401
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    @property
    def channel_id2name(self) -> dict[int, str]:
        return self._channel_id2name

    @channel_id2name.setter
    def channel_id2name(self, value: Any) -> None:  # noqa: ARG002, ANN401
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    @property
    def dev_channel(self) -> TextChannel | Thread:
        if self._dev_channel is None:
            self._dev_channel = self.get_textchannel_or_thread_from_id(
                _id=self._dev_channel_id,
            )
        return self._dev_channel

    @dev_channel.setter
    def dev_channel(self, value: Any) -> None:  # noqa: ARG002, ANN401
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    @property
    def log_channel(self) -> TextChannel | Thread:
        if self._log_channel is None:
            self._log_channel = self.get_textchannel_or_thread_from_id(
                _id=self._log_channel_id,
            )
        return self._log_channel

    @log_channel.setter
    def log_channel(self, value: Any) -> None:  # noqa: ARG002, ANN401
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    def get_textchannel_or_thread_from_id(
        self,
        *,
        _id: int,
    ) -> TextChannel | Thread:
        """idからサーバー内のGuildChannelを取得する

        Args:
            _id (int): ChannelId

        Returns:
            GuildChannel: Channel
        """
        # return cached channel if exists
        if _id in self._cached_channel_from_id:
            return self._cached_channel_from_id[_id]

        # get channel from discord api
        channel_from_key = self.bot.get_channel(_id)
        if channel_from_key is None:
            msg = f"[Error] No match channel from ChannelId: {_id}"
            self._logger.error(msg)
            raise KeyError(msg)
        if not isinstance(channel_from_key, (TextChannel, Thread)):
            msg = f"[Error] No TextChannel or Thread from ChannelId: {_id}"
            self._logger.error(msg)
            raise KeyError(msg)
        self._cached_channel_from_id[_id] = channel_from_key
        return channel_from_key

    def get_channel_from_key(
        self,
        *,
        _id: int | None = None,
        channel_name: str | None = None,
    ) -> GuildChannel:
        """idかチャンネル名のどちらかからサーバー内のGuildChannelを取得する

        Args:
            _id (int): ChannelId
            channel_name (str): ChannelName

        Returns:
            GuildChannel: Channel
        """
        if (_id is None) and (channel_name is None):
            msg = "Invalid arguments: Both of 'id' and 'channel_name' are None"
            self._logger.error(msg)
            raise ValueError(msg)

        # 現在、_id優先での探索となる。両方指定でエラーとしたい場合はコメントアウトする。
        # if _id is not None and channel_name is not None:
        #     msg = "Invalid arguments: Both of 'id' and 'channel_name' are not None"
        #     self._logger.error(msg)
        #     raise ValueError(msg)

        # id is not None
        if _id is not None:
            channel_from_key = self.bot.get_channel(_id)
            if channel_from_key is None:
                msg = f"No match: {_id}"
                self._logger.error(msg)
                raise KeyError(msg)
            if not isinstance(channel_from_key, GuildChannel):
                msg = f"Not channel in this server: {_id}"
                self._logger.error(msg)
                raise KeyError(msg)
            return channel_from_key

        # channel_name is not None
        if channel_name is not None:
            results = [channel for channel in self.bot.get_all_channels() if channel.name == channel_name]
            if len(results) > 1:
                msg = f"Too many match: {len(results)} channels has the name."
                self._logger.error(msg)
                raise ValueError(msg)
            if len(results) == 1:
                return results[0]

        msg = f"No match: {channel_name}."
        self._logger.error(msg)
        raise ValueError(msg)
