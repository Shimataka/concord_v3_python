"""Tests for configuration system."""

# mypy: ignore-errors

from pathlib import Path
from unittest import mock

import pytest

from concord.infrastructure.config.from_files import (
    DEFAULT_CHANNEL_LIST_SECTION_NAME,
    DEFAULT_CONFIG_DIR,
    ConfigAPI,
    ConfigArgs,
    ConfigBOT,
)
from concord.model.config import BaseConfigArgs


class TestBaseConfigArgs:
    """Test the BaseConfigArgs class."""

    @mock.patch("concord.model.config.Path")
    def test_init_success(self, mock_path_class: mock.Mock) -> None:
        """Test successful initialization."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".ini"
        mock_path.as_posix.return_value = "/test/config.ini"
        mock_path_class.return_value = mock_path

        mock_logger = mock.Mock()

        with mock.patch(
            "concord.model.config.ConfigParser",
        ) as mock_config_parser:
            mock_parser = mock.Mock()
            mock_config_parser.return_value = mock_parser

            config = BaseConfigArgs(mock_path, mock_logger)

            assert config.filepath == mock_path
            assert config.config == mock_parser  # type: ignore[reportPrivateUsage]
            assert config._logger == mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            mock_parser.read.assert_called_once()

    @mock.patch("concord.model.config.Path")
    def test_init_file_not_found(self, mock_path_class: mock.Mock) -> None:
        """Test initialization with non-existent file."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = False
        mock_path.absolute.return_value = mock_path
        mock_path.as_posix.return_value = "/test/nonexistent.ini"
        mock_path_class.return_value = mock_path

        mock_logger = mock.Mock()

        with pytest.raises(FileNotFoundError):
            BaseConfigArgs(mock_path, mock_logger, is_required=True)

        mock_logger.error.assert_called_once()

    @mock.patch("concord.model.config.Path")
    def test_init_not_a_file(self, mock_path_class: mock.Mock) -> None:
        """Test initialization with directory instead of file."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        mock_path.absolute.return_value = mock_path
        mock_path.as_posix.return_value = "/test/directory"
        mock_path_class.return_value = mock_path

        mock_logger = mock.Mock()

        with pytest.raises(FileNotFoundError):
            BaseConfigArgs(mock_path, mock_logger, is_required=True)

        mock_logger.error.assert_called_once()

    @mock.patch("concord.model.config.Path")
    def test_init_not_ini_file(self, mock_path_class: mock.Mock) -> None:
        """Test initialization with non-INI file."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".txt"
        mock_path.absolute.return_value = mock_path
        mock_path.as_posix.return_value = "/test/config.txt"
        mock_path_class.return_value = mock_path

        mock_logger = mock.Mock()

        with pytest.raises(ValueError, match="Error: Not ini file: /test/config.txt"):
            BaseConfigArgs(mock_path, mock_logger, is_required=True)

        mock_logger.error.assert_called_once()

    def test_get_success(self) -> None:
        """Test successful get operation."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".ini"
        mock_path.as_posix.return_value = "/test/config.ini"

        mock_logger = mock.Mock()

        with mock.patch("concord.model.config.ConfigParser") as mock_config_parser:
            mock_parser = mock.Mock()
            mock_parser.has_section.return_value = True
            mock_parser.has_option.return_value = True
            mock_parser.__getitem__ = mock.Mock(return_value={"option": "value"})
            mock_config_parser.return_value = mock_parser

            config = BaseConfigArgs(mock_path, mock_logger)
            result = config.get(section="test_section", option="option")

            assert result == "value"

    def test_get_section_not_found(self) -> None:
        """Test get operation with missing section."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".ini"
        mock_path.as_posix.return_value = "/test/config.ini"
        mock_path.absolute.return_value = mock_path

        mock_logger = mock.Mock()

        with mock.patch("concord.model.config.ConfigParser") as mock_config_parser:
            mock_parser = mock.Mock()
            mock_parser.has_section.return_value = False
            mock_config_parser.return_value = mock_parser

            config = BaseConfigArgs(mock_path, mock_logger)

            with pytest.raises(ValueError, match="Not found: /test/config.inisection=missing_section, option=option"):
                config.get(section="missing_section", option="option")

            mock_logger.error.assert_called_once()

    def test_set_value_success(self) -> None:
        """Test successful set_value operation."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".ini"
        mock_path.as_posix.return_value = "/test/config.ini"

        mock_logger = mock.Mock()

        with mock.patch("concord.model.config.ConfigParser") as mock_config_parser:
            mock_parser = mock.Mock()
            mock_parser.has_section.return_value = True
            mock_section = mock.Mock()
            mock_section.__setitem__ = mock.Mock()
            mock_parser.__getitem__ = mock.Mock(return_value=mock_section)
            mock_config_parser.return_value = mock_parser

            config = BaseConfigArgs(mock_path, mock_logger)
            config.set_value(section="test_section", option="option", value="new_value")

            mock_section.__setitem__.assert_called_once_with("option", "new_value")

    def test_set_value_section_not_found(self) -> None:
        """Test set_value operation with missing section."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".ini"
        mock_path.as_posix.return_value = "/test/config.ini"
        mock_path.absolute.return_value = mock_path

        mock_logger = mock.Mock()

        with mock.patch("concord.model.config.ConfigParser") as mock_config_parser:
            mock_parser = mock.Mock()
            mock_parser.has_section.return_value = False
            mock_config_parser.return_value = mock_parser

            config = BaseConfigArgs(mock_path, mock_logger)

            with pytest.raises(KeyError):
                config.set_value(section="missing_section", option="option", value="value")

            mock_logger.error.assert_called_once()

    def test_write(self) -> None:
        """Test write operation."""
        mock_path = mock.Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.suffix = ".ini"
        mock_path.as_posix.return_value = "/test/config.ini"

        mock_logger = mock.Mock()

        with mock.patch("concord.model.config.ConfigParser") as mock_config_parser:
            mock_parser = mock.Mock()
            mock_config_parser.return_value = mock_parser

            mock_file = mock.mock_open()
            mock_path.open.return_value = mock_file.return_value

            config = BaseConfigArgs(mock_path, mock_logger)
            config.write()

            mock_path.open.assert_called_once_with("w", encoding="utf-8")
            mock_parser.write.assert_called_once()


class TestConfigAPI:
    """Test the ConfigAPI class."""

    @mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__")
    def test_init_with_default_path(self, mock_super_init: mock.Mock) -> None:
        """Test ConfigAPI initialization with default path."""
        mock_super_init.return_value = None
        mock_logger = mock.Mock()

        _ = ConfigAPI(logger=mock_logger)

        expected_path = DEFAULT_CONFIG_DIR / "API.ini"
        mock_super_init.assert_called_once_with(filepath=expected_path, logger=mock_logger)

    @mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__")
    def test_init_with_custom_path(self, mock_super_init: mock.Mock) -> None:
        """Test ConfigAPI initialization with custom path."""
        mock_super_init.return_value = None
        mock_logger = mock.Mock()
        custom_path = Path("/custom/api.ini")

        _ = ConfigAPI(logger=mock_logger, filepath=custom_path)

        mock_super_init.assert_called_once_with(filepath=custom_path, logger=mock_logger)

    def test_get_api_token(self) -> None:
        """Test get_api_token method."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigAPI(logger=mock_logger)
            config.get = mock.Mock(return_value="test_token")

            result = config.get_api_token("developer", "key")

            assert result == "test_token"
            config.get.assert_called_once_with(section="developer", option="key")


class TestConfigBOT:
    """Test the ConfigBOT class."""

    @mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__")
    def test_init_with_default_path(self, mock_super_init: mock.Mock) -> None:
        """Test ConfigBOT initialization with default path."""
        mock_super_init.return_value = None
        mock_logger = mock.Mock()

        config = ConfigBOT(bot_name="testbot", logger=mock_logger)

        expected_path = DEFAULT_CONFIG_DIR / "testbot.ini"
        mock_super_init.assert_called_once_with(
            filepath=expected_path,
            logger=mock_logger,
            is_required=True,
        )
        assert config._channel_list_section_name == DEFAULT_CHANNEL_LIST_SECTION_NAME  # noqa: SLF001 # type: ignore[reportPrivateUsage]

    def test_name_property(self) -> None:
        """Test name property getter."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config.get = mock.Mock(return_value="Test Bot")

            result = config.name

            assert result == "Test Bot"
            config.get.assert_called_once_with(section="Discord.Bot", option="name")

    def test_name_property_setter_raises_error(self) -> None:
        """Test name property setter raises error."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            with pytest.raises(NameError):
                config.name = "New Name"

            mock_logger.error.assert_called_once()

    def test_discord_token_property(self) -> None:
        """Test discord_token property getter."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config.get = mock.Mock(return_value="test_token")

            result = config.discord_token

            assert result == "test_token"
            config.get.assert_called_once_with(section="Discord.API", option="token")

    def test_tool_exclusion_property_success(self) -> None:
        """Test tool_exclusion property with valid exclusions."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            config.get = mock.Mock(return_value="tool1,tool2 tool3")

            result = config.tool_exclusion

            assert result == ["tool1", "tool2", "tool3"]
            config.get.assert_called_once_with(section="Discord.Tool", option="exclusions")
            mock_logger.info.assert_called_once()

    def test_tool_exclusion_property_key_error(self) -> None:
        """Test tool_exclusion property with missing key."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            config.get = mock.Mock(side_effect=KeyError("Not found"))

            result = config.tool_exclusion

            assert result == []
            mock_logger.exception.assert_called_once()

    def test_get_default_channel_id_success(self) -> None:
        """Test get_default_channel_id with valid channel."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config.get = mock.Mock(return_value="123456789")

            result = config.get_default_channel_id("dev_channel")

            assert result == 123456789
            config.get.assert_called_once_with(section="Discord.DefaultChannel", option="dev_channel")

    def test_get_default_channel_id_key_error(self) -> None:
        """Test get_default_channel_id with missing key."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            config.get = mock.Mock(side_effect=KeyError("Not found"))

            with pytest.raises(KeyError):
                config.get_default_channel_id("missing_channel")  # type: ignore[reportPrivateUsage]

            mock_logger.exception.assert_called_once()

    def test_get_channel_to_id_mapping_success(self) -> None:
        """Test get_channel_to_id_mapping with valid mapping."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            mock_config = mock.Mock()
            mock_config.has_section.return_value = True
            mock_config.options.return_value = ["channel1", "channel2"]
            mock_config.__getitem__ = mock.Mock(return_value={"channel1": "123", "channel2": "456"})
            config._config = mock_config  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            result = config.get_channel_to_id_mapping()

            expected = {"channel1": 123, "channel2": 456}
            assert result == expected

    def test_get_channel_to_id_mapping_no_section(self) -> None:
        """Test get_channel_to_id_mapping with missing section."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            mock_config = mock.Mock()
            mock_config.has_section.return_value = False
            config._config = mock_config  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            result = config.get_channel_to_id_mapping()

            assert result == {}
            mock_logger.warning.assert_called_once()

    def test_get_id_to_channel_mapping_success(self) -> None:
        """Test get_id_to_channel_mapping with valid mapping."""
        mock_logger = mock.Mock()

        with mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs.__init__"):
            config = ConfigBOT(bot_name="testbot", logger=mock_logger)
            config._logger = mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            mock_config = mock.Mock()
            mock_config.has_section.return_value = True
            mock_config.options.return_value = ["channel1", "channel2"]
            mock_config.__getitem__ = mock.Mock(return_value={"channel1": "123", "channel2": "456"})
            config._config = mock_config  # noqa: SLF001 # type: ignore[reportPrivateUsage]

            result = config.get_id_to_channel_mapping()

            expected = {123: "channel1", 456: "channel2"}
            assert result == expected


class TestConfigArgs:
    """Test the ConfigArgs class."""

    @mock.patch("concord.infrastructure.config.from_files.ConfigBOT")
    @mock.patch("concord.infrastructure.config.from_files.ConfigAPI")
    def test_init(self, mock_config_api: mock.Mock, mock_config_bot: mock.Mock) -> None:
        """Test ConfigArgs initialization."""
        mock_logger = mock.Mock()
        mock_api_instance = mock.Mock()
        mock_bot_instance = mock.Mock()
        mock_config_api.return_value = mock_api_instance
        mock_config_bot.return_value = mock_bot_instance

        config = ConfigArgs(bot_name="testbot", logger=mock_logger)

        assert config._logger == mock_logger  # noqa: SLF001 # type: ignore[reportPrivateUsage]
        assert config.api == mock_api_instance
        assert config.bot == mock_bot_instance

        mock_config_api.assert_called_once_with(logger=mock_logger, filepath=None)
        mock_config_bot.assert_called_once_with(bot_name="testbot", logger=mock_logger, filepath=None)

    @mock.patch("concord.infrastructure.config.from_files.BaseConfigArgs")
    def test_load_config_from(self, mock_base_config: mock.Mock) -> None:
        """Test load_config_from method."""
        mock_logger = mock.Mock()
        mock_base_instance = mock.Mock()
        mock_base_config.return_value = mock_base_instance

        with (
            mock.patch("concord.infrastructure.config.from_files.ConfigBOT"),
            mock.patch("concord.infrastructure.config.from_files.ConfigAPI"),
        ):
            config = ConfigArgs(bot_name="testbot", logger=mock_logger)

            result = config.load_config_from(file_stem="custom")

            assert result == mock_base_instance
            expected_path = DEFAULT_CONFIG_DIR / "custom.ini"
            mock_base_config.assert_called_once_with(filepath=expected_path, logger=mock_logger)
