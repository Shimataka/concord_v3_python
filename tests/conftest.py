"""Pytest configuration and shared fixtures."""

import logging
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture
def mock_logger() -> mock.Mock:
    """Provide a mock logger for testing."""
    return mock.Mock(spec=logging.Logger)


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def sample_config_content() -> str:
    """Provide sample INI config file content."""
    return """
[Discord.Bot]
name = test_bot
description = A test Discord bot

[Discord.API]
token = test_token_123

[Discord.DefaultChannel]
dev_channel = 123456789
log_channel = 987654321

[Discord.Channel]
general = 111111111
announcements = 222222222

[Discord.Tool]
exclusions = tool1, tool2 tool3
"""


@pytest.fixture
def mock_config_file(tmp_path: Path, sample_config_content: str) -> Path:
    """Create a temporary config file for testing."""
    config_file = tmp_path / "test_bot.ini"
    config_file.write_text(sample_config_content)
    return config_file


@pytest.fixture
def mock_api_config_content() -> str:
    """Provide sample API config file content."""
    return """
[OpenAI]
api_key = test_api_key_123

[Discord]
webhook_url = https://discord.com/api/webhooks/test
"""


@pytest.fixture
def mock_api_config_file(tmp_path: Path, mock_api_config_content: str) -> Path:
    """Create a temporary API config file for testing."""
    config_file = tmp_path / "API.ini"
    config_file.write_text(mock_api_config_content)
    return config_file
