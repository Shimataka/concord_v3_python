"""Tests for Agent class."""

# mypy: ignore-errors

import logging
from pathlib import Path
from unittest import mock

import pytest
from discord import Intents
from discord.ext.commands import Cog

from concord.infrastructure.discord.agent import Agent
from concord.model.import_class import LoadedClass


class TestAgent:
    """Test the Agent class."""

    @mock.patch("concord.infrastructure.discord.agent.on_launch")
    @mock.patch("concord.infrastructure.discord.agent.get_logger")
    @mock.patch("concord.infrastructure.discord.agent.ConfigArgs")
    @mock.patch("concord.infrastructure.discord.agent.Bot")
    @mock.patch("concord.infrastructure.discord.agent.CachedChannels")
    def test_init(
        self,
        mock_cached_channels: mock.Mock,
        mock_bot_class: mock.Mock,
        mock_config_args: mock.Mock,
        mock_get_logger: mock.Mock,
        mock_on_launch: mock.Mock,
    ) -> None:
        """Test Agent initialization."""
        # Setup mocks
        mock_args = mock.Mock()
        mock_args.is_debug = False
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = [Path("/test/tools")]
        mock_on_launch.return_value = mock_args

        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger

        mock_config = mock.Mock()
        mock_config.bot.description = "Test Bot Description"
        mock_config_args.return_value = mock_config

        mock_bot = mock.Mock()
        mock_bot.add_cog = mock.AsyncMock()
        mock_bot.load_extension = mock.AsyncMock()
        mock_bot.start = mock.AsyncMock()
        mock_bot_class.return_value = mock_bot

        mock_channels = mock.Mock()
        mock_cached_channels.return_value = mock_channels

        # Create Agent
        agent = Agent()

        # Verify initialization
        mock_on_launch.assert_called_once()
        mock_get_logger.assert_called_once_with(name="test_bot", level=logging.INFO, log_dir=None)
        mock_config_args.assert_called_once_with(bot_name="test_bot", logger=mock_logger, config_dir=None)

        # Verify Bot creation
        mock_bot_class.assert_called_once_with(
            intents=Intents.all(),
            command_prefix="/",
            description="Test Bot Description",
        )

        # Verify CachedChannels creation
        mock_cached_channels.assert_called_once_with(
            bot=mock_bot,
            config=mock_config,
            logger=mock_logger,
        )

        # Verify attributes
        assert agent.logger == mock_logger  # type: ignore[reportPrivateUsage]
        assert agent._tool_directory_paths == [Path("/test/tools")]  # noqa: SLF001 # type: ignore[reportPrivateUsage]
        assert agent.config == mock_config  # type: ignore[reportPrivateUsage]
        assert agent.bot == mock_bot  # type: ignore[reportPrivateUsage]
        assert agent.cached_channels == mock_channels  # type: ignore[reportPrivateUsage]

        # Verify bot event registration
        mock_bot.event.assert_called_once()

    @mock.patch("concord.infrastructure.discord.agent.on_launch")
    @mock.patch("concord.infrastructure.discord.agent.get_logger")
    @mock.patch("concord.infrastructure.discord.agent.ConfigArgs")
    @mock.patch("concord.infrastructure.discord.agent.Bot")
    @mock.patch("concord.infrastructure.discord.agent.CachedChannels")
    def test_init_debug_mode(
        self,
        mock_cached_channels: mock.Mock,
        mock_bot_class: mock.Mock,
        mock_config_args: mock.Mock,
        mock_get_logger: mock.Mock,
        mock_on_launch: mock.Mock,
    ) -> None:
        """Test Agent initialization in debug mode."""
        mock_args = mock.Mock()
        mock_args.is_debug = True
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = [Path("/test/tools")]
        mock_on_launch.return_value = mock_args

        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger

        mock_config = mock.Mock()
        mock_config.bot.description = "Test Bot Description"
        mock_config_args.return_value = mock_config

        mock_bot = mock.Mock()
        mock_bot.add_cog = mock.AsyncMock()
        mock_bot.load_extension = mock.AsyncMock()
        mock_bot.start = mock.AsyncMock()
        mock_bot_class.return_value = mock_bot

        mock_channels = mock.Mock()
        mock_cached_channels.return_value = mock_channels

        _ = Agent()  # type: ignore[reportPrivateUsage]

        mock_get_logger.assert_called_once_with(name="test_bot", level=logging.DEBUG, log_dir=None)

    @pytest.mark.asyncio
    async def test_greetings_success(self) -> None:
        """Test greetings method with valid bot user."""
        with (
            mock.patch("concord.infrastructure.discord.agent.on_launch"),
            mock.patch("concord.infrastructure.discord.agent.get_logger"),
            mock.patch("concord.infrastructure.discord.agent.ConfigArgs"),
            mock.patch("concord.infrastructure.discord.agent.Bot"),
            mock.patch("concord.infrastructure.discord.agent.CachedChannels"),
        ):
            agent = Agent()
            agent._tool_directory_paths = [Path("/test/tools")]  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            agent.greetings = mock.AsyncMock(return_value="Logged in as TestBot (12345)Guilds: 2Channels: 3")

            # Mock bot user and guilds
            mock_user = mock.Mock()
            mock_user.name = "TestBot"
            mock_user.id = 12345

            mock_guild1 = mock.Mock()
            mock_guild2 = mock.Mock()

            mock_channel1 = mock.Mock()
            mock_channel2 = mock.Mock()
            mock_channel3 = mock.Mock()

            agent.bot.user = mock_user  # type: ignore[reportPrivateUsage]
            agent.bot.guilds = [mock_guild1, mock_guild2]  # type: ignore[reportPrivateUsage]
            agent.bot.get_all_channels.return_value = [mock_channel1, mock_channel2, mock_channel3]  # type: ignore[reportPrivateUsage]

            result = await agent.greetings()

            expected = "Logged in as TestBot (12345)Guilds: 2Channels: 3"
            assert result == expected

    @pytest.mark.asyncio
    async def test_greetings_user_none(self) -> None:
        """Test greetings method when bot user is None."""
        with (
            mock.patch("concord.infrastructure.discord.agent.on_launch"),
            mock.patch("concord.infrastructure.discord.agent.get_logger") as mock_get_logger,
            mock.patch("concord.infrastructure.discord.agent.ConfigArgs"),
            mock.patch("concord.infrastructure.discord.agent.Bot"),
            mock.patch("concord.infrastructure.discord.agent.CachedChannels"),
        ):
            mock_logger = mock.Mock()
            mock_get_logger.return_value = mock_logger

            agent = Agent()
            agent.bot.user = None  # type: ignore[reportPrivateUsage]

            with pytest.raises(ValueError, match="User is None") as exc_info:
                await agent.greetings()

            assert "User is None" in str(exc_info.value)
            mock_logger.error.assert_called_once_with("User is None")

    @pytest.mark.asyncio
    async def test_on_ready(self) -> None:
        """Test on_ready method."""
        with (
            mock.patch("concord.infrastructure.discord.agent.on_launch"),
            mock.patch("concord.infrastructure.discord.agent.get_logger") as mock_get_logger,
            mock.patch("concord.infrastructure.discord.agent.ConfigArgs"),
            mock.patch("concord.infrastructure.discord.agent.Bot") as mock_bot_class,
            mock.patch("concord.infrastructure.discord.agent.CachedChannels") as mock_cached_channels_class,
            mock.patch("concord.infrastructure.discord.agent.import_classes_from_directory") as mock_import,
            mock.patch("concord.infrastructure.discord.agent.OnConnecting") as mock_on_connecting,
            mock.patch("concord.infrastructure.discord.agent.OnReady") as mock_on_ready_class,
            mock.patch("concord.infrastructure.discord.agent.DiscordLogHandler") as mock_log_handler,
        ):
            # Setup mocks
            mock_logger = mock.Mock()
            mock_get_logger.return_value = mock_logger

            mock_bot = mock.Mock()
            mock_bot.add_cog = mock.AsyncMock()
            mock_bot.load_extension = mock.AsyncMock()
            mock_bot.start = mock.AsyncMock()
            mock_bot_class.return_value = mock_bot

            mock_dev_channel = mock.Mock()
            mock_dev_channel.send = mock.AsyncMock()
            mock_log_channel = mock.Mock()
            mock_log_channel.send = mock.AsyncMock()
            mock_cached_channels = mock.Mock()
            mock_cached_channels.dev_channel = mock_dev_channel
            mock_cached_channels.log_channel = mock_log_channel
            mock_cached_channels_class.return_value = mock_cached_channels

            # Mock import_classes_from_directory to return some tools
            mock_tool1 = LoadedClass[type[Cog]](
                name="Tool1",
                class_type=mock.Mock(__name__="Tool1"),  # type: ignore[reportPrivateUsage]
            )
            mock_tool1.class_type.return_value.add_cog = mock.AsyncMock()  # type: ignore[reportPrivateUsage]
            mock_tool1.class_type.return_value.__name__ = "Tool1"  # type: ignore[reportPrivateUsage]
            mock_tool2 = LoadedClass[type[Cog]](
                name="Tool2",
                class_type=mock.Mock(__name__="Tool2"),  # type: ignore[reportPrivateUsage]
            )
            mock_tool2.class_type.return_value.add_cog = mock.AsyncMock()  # type: ignore[reportPrivateUsage]
            mock_tool2.class_type.return_value.__name__ = "Tool2"  # type: ignore[reportPrivateUsage]
            mock_import.return_value = [mock_tool1, mock_tool2]

            # Mock cog instances
            mock_on_connecting_instance = mock.Mock()
            mock_on_connecting.return_value = mock_on_connecting_instance
            mock_on_ready_instance = mock.Mock()
            mock_on_ready_class.return_value = mock_on_ready_instance

            # Mock log handler
            mock_handler = mock.Mock()
            mock_log_handler.return_value = mock_handler

            agent = Agent()
            agent._tool_directory_paths = [Path("/test/tools")]  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            agent.greetings = mock.AsyncMock(return_value="Test greeting message")

            # Call on_ready
            await agent.on_ready()

            # Verify cogs were added
            assert mock_bot.add_cog.call_count == 4
            mock_bot.add_cog.assert_any_call(mock_on_connecting_instance)
            mock_bot.add_cog.assert_any_call(mock_on_ready_instance)
            mock_bot.add_cog.assert_any_call(mock_tool1.class_type(agent=agent))
            mock_bot.add_cog.assert_any_call(mock_tool2.class_type(agent=agent))

            # Verify greetings was called and logged
            agent.greetings.assert_called_once()
            mock_logger.info.assert_called_with("Sent message to dev channel")

            # Verify log handler was added
            mock_log_handler.assert_called_once_with(mock_log_channel)
            mock_logger.addHandler.assert_called_once_with(mock_handler)

            # Verify dev channel messages
            assert mock_dev_channel.send.call_count == 2
            mock_dev_channel.send.assert_any_call("Good morning, Master.\nGood work today.")

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method."""
        with (
            mock.patch("concord.infrastructure.discord.agent.on_launch"),
            mock.patch("concord.infrastructure.discord.agent.get_logger"),
            mock.patch("concord.infrastructure.discord.agent.ConfigArgs") as mock_config_args,
            mock.patch("concord.infrastructure.discord.agent.Bot") as mock_bot_class,
            mock.patch("concord.infrastructure.discord.agent.CachedChannels"),
        ):
            # Setup mocks
            mock_config = mock.Mock()
            mock_config.bot.discord_token = "test_token"  # noqa: S105
            mock_config_args.return_value = mock_config

            mock_bot = mock.Mock()
            mock_bot.add_cog = mock.AsyncMock()
            mock_bot.load_extension = mock.AsyncMock()
            mock_bot.start = mock.AsyncMock()
            mock_bot_class.return_value = mock_bot

            agent = Agent()

            # Call run
            await agent.run()

            # Verify bot.start was called with correct token
            mock_bot.start.assert_called_once_with("test_token")
