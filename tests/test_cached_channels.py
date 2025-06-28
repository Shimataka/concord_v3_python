"""Tests for CachedChannels class."""

import logging
from unittest import mock

import pytest
from discord import Thread
from discord.abc import GuildChannel
from discord.channel import TextChannel
from discord.ext.commands import Bot

from concord.infrastructure.config.from_files import ConfigArgs
from concord.infrastructure.discord.cached_channels import CachedChannels


class TestCachedChannels:
    """Test the CachedChannels class."""

    def create_cached_channels(
        self,
        channel_mappings: dict[str, int] | None = None,
        config_mappings: dict[int, str] | None = None,
    ) -> tuple[CachedChannels, mock.Mock, mock.Mock]:
        """Helper method to create CachedChannels instance with mocks."""
        if channel_mappings is None:
            channel_mappings = {"dev_channel": 123, "log_channel": 456}
        if config_mappings is None:
            config_mappings = {123: "dev_channel", 456: "log_channel"}

        mock_bot = mock.Mock(spec=Bot)
        mock_config = mock.Mock(spec=ConfigArgs)
        mock_config.bot = mock.Mock()
        mock_config.bot.get_channel_to_id_mapping.return_value = channel_mappings
        mock_config.bot.get_id_to_channel_mapping.return_value = config_mappings
        mock_config.bot.get_default_channel_id.side_effect = lambda name: 123 if name == "dev_channel" else 456  # type: ignore[reportPrivateUsage]
        mock_logger = mock.Mock(spec=logging.Logger)

        return CachedChannels(bot=mock_bot, config=mock_config, logger=mock_logger), mock_bot, mock_logger

    def test_init(self) -> None:
        """Test CachedChannels initialization."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        assert cached_channels.bot == mock_bot
        assert cached_channels._logger == mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]
        assert cached_channels.channel_name2id == {"dev_channel": 123, "log_channel": 456}
        assert cached_channels.channel_id2name == {123: "dev_channel", 456: "log_channel"}
        assert cached_channels._dev_channel is None  # noqa: SLF001 # type: ignore[reportPrivateUsage]
        assert cached_channels._log_channel is None  # noqa: SLF001 # type: ignore[reportPrivateUsage]

    def test_channel_name2id_property(self) -> None:
        """Test channel_name2id property getter."""
        cached_channels, _, _ = self.create_cached_channels()

        result = cached_channels.channel_name2id
        assert result == {"dev_channel": 123, "log_channel": 456}

    def test_channel_name2id_setter_raises_error(self) -> None:
        """Test channel_name2id property setter raises error."""
        cached_channels, _, mock_logger = self.create_cached_channels()

        with pytest.raises(NameError):
            cached_channels.channel_name2id = {"new": 123}

        mock_logger.error.assert_called_once()

    def test_channel_id2name_property(self) -> None:
        """Test channel_id2name property getter."""
        cached_channels, _, _ = self.create_cached_channels()

        result = cached_channels.channel_id2name
        assert result == {123: "dev_channel", 456: "log_channel"}

    def test_channel_id2name_setter_raises_error(self) -> None:
        """Test channel_id2name property setter raises error."""
        cached_channels, _, mock_logger = self.create_cached_channels()

        with pytest.raises(NameError):
            cached_channels.channel_id2name = {123: "new_mapping"}

        mock_logger.error.assert_called_once()

    def test_dev_channel_property_lazy_loading(self) -> None:
        """Test dev_channel property lazy loading."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=TextChannel)
        mock_bot.get_channel.return_value = mock_channel

        # First access should trigger lazy loading
        result = cached_channels.dev_channel
        assert result == mock_channel
        mock_bot.get_channel.assert_called_once_with(123)

        # Second access should use cached value
        result2 = cached_channels.dev_channel
        assert result2 == mock_channel
        assert mock_bot.get_channel.call_count == 1

    def test_dev_channel_setter_raises_error(self) -> None:
        """Test dev_channel property setter raises error."""
        cached_channels, _, mock_logger = self.create_cached_channels()

        with pytest.raises(NameError):
            cached_channels.dev_channel = mock.Mock()

        mock_logger.error.assert_called_once()

    def test_log_channel_property_lazy_loading(self) -> None:
        """Test log_channel property lazy loading."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=TextChannel)
        mock_bot.get_channel.return_value = mock_channel

        result = cached_channels.log_channel
        assert result == mock_channel
        mock_bot.get_channel.assert_called_once_with(456)

    def test_log_channel_setter_raises_error(self) -> None:
        """Test log_channel property setter raises error."""
        cached_channels, _, mock_logger = self.create_cached_channels()

        with pytest.raises(NameError):
            cached_channels.log_channel = mock.Mock()

        mock_logger.error.assert_called_once()

    def test_get_default_channel_from_id_success_text_channel(self) -> None:
        """Test get_default_channel_from_id with TextChannel."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=TextChannel)
        mock_bot.get_channel.return_value = mock_channel

        result = cached_channels.get_textchannel_or_thread_from_id(_id=123)

        assert result == mock_channel
        mock_bot.get_channel.assert_called_once_with(123)

    def test_get_default_channel_from_id_success_thread(self) -> None:
        """Test get_default_channel_from_id with Thread."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_thread = mock.Mock(spec=Thread)
        mock_bot.get_channel.return_value = mock_thread

        result = cached_channels.get_textchannel_or_thread_from_id(_id=123)

        assert result == mock_thread
        mock_bot.get_channel.assert_called_once_with(123)

    def test_get_default_channel_from_id_channel_not_found(self) -> None:
        """Test get_default_channel_from_id with non-existent channel."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        mock_bot.get_channel.return_value = None

        with pytest.raises(KeyError):
            cached_channels.get_textchannel_or_thread_from_id(_id=999)

        mock_logger.error.assert_called_once()

    def test_get_default_channel_from_id_wrong_channel_type(self) -> None:
        """Test get_default_channel_from_id with wrong channel type."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        mock_channel = mock.Mock()  # Not TextChannel or Thread
        mock_bot.get_channel.return_value = mock_channel

        with pytest.raises(KeyError):
            cached_channels.get_textchannel_or_thread_from_id(_id=123)

        mock_logger.error.assert_called()

    def test_get_channel_from_id_or_name_by_id_success(self) -> None:
        """Test get_channel_from_key with valid channel ID."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=GuildChannel)
        mock_bot.get_channel.return_value = mock_channel

        result = cached_channels.get_channel_from_id_or_name(_id=123)

        assert result == mock_channel
        mock_bot.get_channel.assert_called_once_with(123)

    def test_get_channel_from_id_or_name_by_id_not_found(self) -> None:
        """Test get_channel_from_key with non-existent channel ID."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        mock_bot.get_channel.return_value = None

        with pytest.raises(KeyError):
            cached_channels.get_channel_from_id_or_name(_id=999)

        mock_logger.error.assert_called_once()

    def test_get_channel_from_id_or_name_by_id_not_guild_channel(self) -> None:
        """Test get_channel_from_key with non-GuildChannel."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        mock_channel = mock.Mock()  # Not GuildChannel
        mock_bot.get_channel.return_value = mock_channel

        with pytest.raises(KeyError):
            cached_channels.get_channel_from_id_or_name(_id=123)

        mock_logger.error.assert_called()

    def test_get_channel_from_id_or_name_by_name_success(self) -> None:
        """Test get_channel_from_key with valid channel name."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=GuildChannel)
        mock_channel.name = "test_channel"
        mock_bot.get_all_channels.return_value = [mock_channel]

        result = cached_channels.get_channel_from_id_or_name(channel_name="test_channel")

        assert result == mock_channel

    def test_get_channel_from_id_or_name_by_name_multiple_matches(self) -> None:
        """Test get_channel_from_key with multiple matching channel names."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        mock_channel1 = mock.Mock(spec=GuildChannel)
        mock_channel1.name = "duplicate"
        mock_channel2 = mock.Mock(spec=GuildChannel)
        mock_channel2.name = "duplicate"
        mock_bot.get_all_channels.return_value = [mock_channel1, mock_channel2]

        with pytest.raises(ValueError, match="Too many match: 2 channels has the name."):
            cached_channels.get_channel_from_id_or_name(channel_name="duplicate")

        mock_logger.error.assert_called()

    def test_get_channel_from_id_or_name_by_name_no_matches(self) -> None:
        """Test get_channel_from_key with no matching channel names."""
        cached_channels, mock_bot, mock_logger = self.create_cached_channels()

        mock_channel = mock.Mock(spec=GuildChannel)
        mock_channel.name = "other_channel"
        mock_bot.get_all_channels.return_value = [mock_channel]

        with pytest.raises(ValueError, match="No match: nonexistent."):
            cached_channels.get_channel_from_id_or_name(channel_name="nonexistent")

        mock_logger.error.assert_called()

    def test_get_channel_from_id_or_name_both_args_none(self) -> None:
        """Test get_channel_from_key with both arguments None."""
        cached_channels, _, mock_logger = self.create_cached_channels()

        with pytest.raises(ValueError, match="Invalid arguments: Both of 'id' and 'channel_name' are None"):
            cached_channels.get_channel_from_id_or_name()

        mock_logger.error.assert_called_once()

    def test_get_channel_from_id_or_name_id_takes_priority(self) -> None:
        """Test get_channel_from_key with both arguments provided (ID takes priority)."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=GuildChannel)
        mock_bot.get_channel.return_value = mock_channel

        result = cached_channels.get_channel_from_id_or_name(_id=123, channel_name="test_channel")

        assert result == mock_channel
        mock_bot.get_channel.assert_called_once_with(123)
        # get_all_channels should not be called since ID takes priority
        mock_bot.get_all_channels.assert_not_called()

    def test_get_channel_from_key_success(self) -> None:
        """Test get_channel_from_key with valid key."""
        cached_channels, mock_bot, _ = self.create_cached_channels()

        mock_channel = mock.Mock(spec=GuildChannel)
        mock_bot.get_channel.return_value = mock_channel

        result = cached_channels.get_channel_from_key(key="dev_channel")

        assert result == mock_channel
        mock_bot.get_channel.assert_called_once_with(123)

    def test_get_channel_from_key_not_found(self) -> None:
        """Test get_channel_from_key with non-existent key."""
        cached_channels, _, mock_logger = self.create_cached_channels()

        with pytest.raises(KeyError, match="No match: nonexistent_key"):
            cached_channels.get_channel_from_key(key="nonexistent_key")

        mock_logger.error.assert_called_once_with("No match: nonexistent_key")
