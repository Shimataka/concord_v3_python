"""Tests for logger factory module."""

import logging
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from concord.infrastructure.logging.logger_factory import (
    BACKGROUND_LOG_FORMATTER,
    BACKGROUND_LOG_LEVEL,
    DEBUG_LOG_FORMATTER,
    DEFAULT_LOG_DIR,
    get_background_log,
    get_logger,
    my_logger,
)


class TestLoggerFactory:
    """Test the logger factory functions."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @mock.patch("concord.infrastructure.logging.logger_factory.getLogger")
    @mock.patch("concord.infrastructure.logging.logger_factory.TimedRotatingFileHandler")
    @mock.patch("concord.infrastructure.logging.logger_factory.Formatter")
    def test_get_background_log(
        self,
        mock_formatter_class: mock.Mock,
        mock_handler_class: mock.Mock,
        mock_get_logger: mock.Mock,
    ) -> None:
        """Test get_background_log function."""
        # Setup mocks
        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger

        mock_handler = mock.Mock()
        mock_handler_class.return_value = mock_handler

        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        log_dir = self.temp_dir / "logs"

        # Call function
        result = get_background_log("test_logger", log_dir)

        # Verify logger setup
        mock_get_logger.assert_called_once_with("test_logger")
        mock_logger.setLevel.assert_called_once_with(BACKGROUND_LOG_LEVEL)

        # Verify handler setup
        expected_log_path = (log_dir / "test_logger.background.log").as_posix()
        mock_handler_class.assert_called_once_with(
            expected_log_path,
            when="midnight",
            interval=7,
            backupCount=4,
            encoding="utf-8",
        )

        # Verify formatter setup
        mock_formatter_class.assert_called_once_with(BACKGROUND_LOG_FORMATTER)
        mock_handler.setFormatter.assert_called_once_with(mock_formatter)

        # Verify handler added to logger
        mock_logger.addHandler.assert_called_once_with(mock_handler)

        assert result == mock_logger

    @mock.patch("concord.infrastructure.logging.logger_factory.getLogger")
    @mock.patch("concord.infrastructure.logging.logger_factory.FileHandler")
    @mock.patch("concord.infrastructure.logging.logger_factory.Formatter")
    def test_my_logger(
        self,
        mock_formatter_class: mock.Mock,
        mock_handler_class: mock.Mock,
        mock_get_logger: mock.Mock,
    ) -> None:
        """Test my_logger function."""
        # Setup mocks
        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger

        mock_handler = mock.Mock()
        mock_handler_class.return_value = mock_handler

        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        log_dir = self.temp_dir / "logs"
        log_level = logging.DEBUG

        # Call function
        result = my_logger("test_logger", log_level, log_dir)

        # Verify logger setup
        mock_get_logger.assert_called_once_with("test_logger")
        mock_logger.setLevel.assert_called_once_with(log_level)

        # Verify handler setup
        expected_log_path = (log_dir / "test_logger.log").as_posix()
        mock_handler_class.assert_called_once_with(expected_log_path, encoding="utf-8")

        # Verify formatter setup
        mock_formatter_class.assert_called_once_with(DEBUG_LOG_FORMATTER)
        mock_handler.setFormatter.assert_called_once_with(mock_formatter)

        # Verify handler added to logger
        mock_logger.addHandler.assert_called_once_with(mock_handler)

        assert result == mock_logger

    @mock.patch("concord.infrastructure.logging.logger_factory.get_background_log")
    @mock.patch("concord.infrastructure.logging.logger_factory.my_logger")
    def test_get_logger_background_level(
        self,
        mock_my_logger_func: mock.Mock,
        mock_get_background_log: mock.Mock,
    ) -> None:
        """Test get_logger function with background log level."""
        mock_logger = mock.Mock()
        mock_get_background_log.return_value = mock_logger

        log_dir = self.temp_dir / "logs"

        # Test with level equal to BACKGROUND_LOG_LEVEL
        result = get_logger("test_logger", BACKGROUND_LOG_LEVEL, log_dir)

        mock_get_background_log.assert_called_once_with("test_logger", log_dir)
        mock_my_logger_func.assert_not_called()
        assert result == mock_logger

    @mock.patch("concord.infrastructure.logging.logger_factory.get_background_log")
    @mock.patch("concord.infrastructure.logging.logger_factory.my_logger")
    def test_get_logger_higher_level(
        self,
        mock_my_logger_func: mock.Mock,
        mock_get_background_log: mock.Mock,
    ) -> None:
        """Test get_logger function with level higher than background."""
        mock_background_logger = mock.Mock()
        mock_get_background_log.return_value = mock_background_logger

        mock_debug_logger = mock.Mock()
        mock_my_logger_func.return_value = mock_debug_logger

        log_dir = self.temp_dir / "logs"
        debug_level = logging.DEBUG

        # Test with level higher than BACKGROUND_LOG_LEVEL
        result = get_logger("test_logger", debug_level, log_dir)

        mock_get_background_log.assert_called_once_with("test_logger", log_dir)
        mock_my_logger_func.assert_called_once_with("test_logger", debug_level, log_dir)
        assert result == mock_debug_logger

    @mock.patch("concord.infrastructure.logging.logger_factory.get_background_log")
    @mock.patch("concord.infrastructure.logging.logger_factory.my_logger")
    def test_get_logger_default_parameters(
        self,
        mock_my_logger_func: mock.Mock,
        mock_get_background_log: mock.Mock,
    ) -> None:
        """Test get_logger function with default parameters."""
        mock_logger = mock.Mock()
        mock_get_background_log.return_value = mock_logger

        # Test with default parameters
        result = get_logger("test_logger")

        mock_get_background_log.assert_called_once_with("test_logger", DEFAULT_LOG_DIR)
        mock_my_logger_func.assert_not_called()
        assert result == mock_logger

    @mock.patch("concord.infrastructure.logging.logger_factory.get_background_log")
    @mock.patch("concord.infrastructure.logging.logger_factory.my_logger")
    def test_get_logger_lower_level(
        self,
        mock_my_logger_func: mock.Mock,
        mock_get_background_log: mock.Mock,
    ) -> None:
        """Test get_logger function with level lower than background."""
        mock_logger = mock.Mock()
        mock_get_background_log.return_value = mock_logger

        log_dir = self.temp_dir / "logs"

        # Test with level lower than BACKGROUND_LOG_LEVEL (which is INFO)
        debug_level = logging.DEBUG

        _ = get_logger("test_logger", debug_level, log_dir)

        mock_get_background_log.assert_called_once_with("test_logger", log_dir)
        mock_my_logger_func.assert_called_once_with("test_logger", debug_level, log_dir)

    def test_constants(self) -> None:
        """Test that constants are properly defined."""
        assert BACKGROUND_LOG_LEVEL == logging.INFO
        assert isinstance(BACKGROUND_LOG_FORMATTER, str)
        assert isinstance(DEBUG_LOG_FORMATTER, str)
        assert isinstance(DEFAULT_LOG_DIR, Path)

        # Verify formatter strings contain expected placeholders
        assert "%(asctime)s" in BACKGROUND_LOG_FORMATTER
        assert "%(name)s" in BACKGROUND_LOG_FORMATTER
        assert "%(levelname)s" in BACKGROUND_LOG_FORMATTER
        assert "%(message)s" in BACKGROUND_LOG_FORMATTER

        assert "%(asctime)s" in DEBUG_LOG_FORMATTER
        assert "%(name)s" in DEBUG_LOG_FORMATTER
        assert "%(levelname)s" in DEBUG_LOG_FORMATTER
        assert "%(message)s" in DEBUG_LOG_FORMATTER
        assert "%(filename)s" in DEBUG_LOG_FORMATTER
        assert "%(lineno)d" in DEBUG_LOG_FORMATTER
        assert "%(module)s" in DEBUG_LOG_FORMATTER
        assert "%(funcName)s" in DEBUG_LOG_FORMATTER
