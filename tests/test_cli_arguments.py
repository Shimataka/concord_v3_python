"""Tests for CLI arguments module."""

from pathlib import Path
from unittest import mock

import pytest

from concord.cli.arguments import on_launch
from concord.model.argument import Args


class TestArgs:
    """Test the Args dataclass."""

    def test_args_creation(self) -> None:
        """Test Args dataclass creation."""
        args = Args(
            bot_name="test_bot",
            tool_directory_paths=[Path("/test/path1"), Path("/test/path2")],
            is_debug=True,
        )

        assert args.bot_name == "test_bot"
        assert args.tool_directory_paths == [Path("/test/path1"), Path("/test/path2")]
        assert args.is_debug is True


class TestOnLaunch:
    """Test the on_launch function."""

    @mock.patch("concord.cli.arguments.ArgumentParser")
    @mock.patch("pathlib.Path.is_dir")
    @mock.patch("pathlib.Path.exists")
    def test_on_launch_success(
        self,
        mock_exists: mock.Mock,
        mock_is_dir: mock.Mock,
        mock_parser_class: mock.Mock,
    ) -> None:
        """Test successful argument parsing."""
        # Setup mock parser
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        # Setup mock parsed args
        mock_args = mock.Mock()
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = "/path/to/tools1 /path/to/tools2"
        mock_args.is_debug = True
        mock_parser.parse_args.return_value = mock_args

        # Setup directory existence mocks
        mock_is_dir.return_value = True
        mock_exists.return_value = True

        # Call function
        result = on_launch()

        # Verify parser setup
        mock_parser_class.assert_called_once()
        assert mock_parser.add_argument.call_count == 3

        # Verify add_argument calls
        call_args = [call[1] for call in mock_parser.add_argument.call_args_list]

        # Check bot-name argument
        bot_name_args = call_args[0]
        assert bot_name_args["type"] == str
        assert bot_name_args["required"] is True

        # Check tool-directory-paths argument
        tool_paths_args = call_args[1]
        assert tool_paths_args["type"] == str
        assert tool_paths_args["required"] is False
        assert tool_paths_args["default"] == ""

        # Check is-debug argument
        debug_args = call_args[2]
        assert debug_args["action"] == "store_true"
        assert debug_args["required"] is False
        assert debug_args["default"] is False

        # Verify result
        assert isinstance(result, Args)
        assert result.bot_name == "test_bot"
        assert result.tool_directory_paths == [Path("/path/to/tools1"), Path("/path/to/tools2")]
        assert result.is_debug is True

    @mock.patch("concord.cli.arguments.ArgumentParser")
    @mock.patch("pathlib.Path.is_dir")
    @mock.patch("pathlib.Path.exists")
    def test_on_launch_single_tool_path(
        self,
        mock_exists: mock.Mock,
        mock_is_dir: mock.Mock,
        mock_parser_class: mock.Mock,
    ) -> None:
        """Test argument parsing with single tool path."""
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = mock.Mock()
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = "/single/path"
        mock_args.is_debug = False
        mock_parser.parse_args.return_value = mock_args

        # Setup directory existence mocks
        mock_is_dir.return_value = True
        mock_exists.return_value = True

        result = on_launch()

        assert result.tool_directory_paths == [Path("/single/path")]
        assert result.is_debug is False

    @mock.patch("concord.cli.arguments.ArgumentParser")
    def test_on_launch_invalid_bot_name_type(self, mock_parser_class: mock.Mock) -> None:
        """Test argument parsing with invalid bot_name type."""
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = mock.Mock()
        mock_args.bot_name = 123  # Invalid type
        mock_args.tool_directory_paths = "/path/to/tools"
        mock_args.is_debug = False
        mock_parser.parse_args.return_value = mock_args

        with pytest.raises(TypeError) as exc_info:
            on_launch()

        assert "bot_name must be a string" in str(exc_info.value)

    @mock.patch("concord.cli.arguments.ArgumentParser")
    def test_on_launch_invalid_tool_paths_type(self, mock_parser_class: mock.Mock) -> None:
        """Test argument parsing with invalid tool_directory_paths type."""
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = mock.Mock()
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = 123  # Invalid type
        mock_args.is_debug = False
        mock_parser.parse_args.return_value = mock_args

        with pytest.raises(TypeError) as exc_info:
            on_launch()

        assert "tool_directory_paths must be a string or list[Path]" in str(exc_info.value)

    @mock.patch("concord.cli.arguments.ArgumentParser")
    @mock.patch("pathlib.Path.is_dir")
    @mock.patch("pathlib.Path.exists")
    def test_on_launch_invalid_debug_type(
        self,
        mock_exists: mock.Mock,
        mock_is_dir: mock.Mock,
        mock_parser_class: mock.Mock,
    ) -> None:
        """Test argument parsing with invalid is_debug type."""
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = mock.Mock()
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = "/path/to/tools"
        mock_args.is_debug = "not_a_bool"  # Invalid type
        mock_parser.parse_args.return_value = mock_args

        # Setup directory existence mocks
        mock_is_dir.return_value = True
        mock_exists.return_value = True

        with pytest.raises(TypeError) as exc_info:
            on_launch()

        assert "is_debug must be a bool" in str(exc_info.value)

    @mock.patch("concord.cli.arguments.ArgumentParser")
    @mock.patch("pathlib.Path.is_dir")
    @mock.patch("pathlib.Path.exists")
    def test_on_launch_empty_tool_paths(
        self,
        mock_exists: mock.Mock,
        mock_is_dir: mock.Mock,
        mock_parser_class: mock.Mock,
    ) -> None:
        """Test argument parsing with empty tool paths string."""
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = mock.Mock()
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = ""
        mock_args.is_debug = False
        mock_parser.parse_args.return_value = mock_args

        # Setup directory existence mocks
        mock_is_dir.return_value = True
        mock_exists.return_value = True

        result = on_launch()

        # Empty string split should result in empty list
        assert result.tool_directory_paths == []

    @mock.patch("concord.cli.arguments.ArgumentParser")
    @mock.patch("pathlib.Path.is_dir")
    @mock.patch("pathlib.Path.exists")
    def test_on_launch_whitespace_in_paths(
        self,
        mock_exists: mock.Mock,
        mock_is_dir: mock.Mock,
        mock_parser_class: mock.Mock,
    ) -> None:
        """Test argument parsing with extra whitespace in paths."""
        mock_parser = mock.Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = mock.Mock()
        mock_args.bot_name = "test_bot"
        mock_args.tool_directory_paths = "  /path1   /path2  /path3  "
        mock_args.is_debug = False
        mock_parser.parse_args.return_value = mock_args

        # Setup directory existence mocks
        mock_is_dir.return_value = True
        mock_exists.return_value = True

        result = on_launch()

        assert set(result.tool_directory_paths) == {Path("/path1"), Path("/path2"), Path("/path3")}
