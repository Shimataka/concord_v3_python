import logging
from configparser import ConfigParser
from pathlib import Path
from typing import Literal


class BaseConfigArgs:
    """設定ファイルの読み込みを行うクラス

    Args:
        filepath (Path): 設定ファイルのパス

    Attributes:
        filepath (Path): 設定ファイルのパス
        config (ConfigParser): 設定ファイルのパーサー (設定値を保持する)
    """

    def __init__(self, filepath: Path, logger: logging.Logger) -> None:
        self.filepath = filepath.resolve()
        self._config = ConfigParser()
        self._logger = logger

        # Check existence
        if not self.filepath.exists():
            msg = f"Error: Not found: {self.filepath.absolute().as_posix()}"
            self._logger.error(msg)
            raise FileNotFoundError(msg)
        if not self.filepath.is_file():
            msg = f"Error: Not a file: {self.filepath.absolute().as_posix()}"
            self._logger.error(msg)
            raise FileNotFoundError(msg)
        if self.filepath.suffix != ".ini":
            msg = f"Error: Not ini file: {self.filepath.absolute().as_posix()}"
            self._logger.error(msg)
            raise ValueError(msg)

        # Parser
        self._config.read(
            filenames=self.filepath.as_posix(),
            encoding="utf-8",
        )

    def get(self, *, section: str, option: str) -> str:
        """設定ファイルから値を取得する

        Args:
            section (str): セクション名
            option (str): オプション名

        Returns:
            str: 値
        """
        if self._config.has_section(
            section=section,
        ) and self._config.has_option(
            section=section,
            option=option,
        ):
            return self._config[section][option]
        msg = f"Not found: {self.filepath.absolute().as_posix()}"
        msg += f"section={section}, option={option}"
        self._logger.error(msg)
        raise ValueError(msg)

    def set_value(self, *, section: str, option: str, value: str) -> None:
        """設定ファイルに値を設定する

        Args:
            section (str): セクション名
            option (str): オプション名
            value (str): 値

        Returns:
            None

        Examples:
            >>> config = BaseConfigArgs(filepath=Path("test.ini"), logger=logging.getLogger())
            >>> config.set_value(section="test", option="test", value="test")
        """
        if self._config.has_section(section):
            self._config[section][option] = value
        else:
            msg = f"Section {section} was not found in {self.filepath.absolute().as_posix()}"
            self._logger.error(msg)
            raise KeyError(msg)

    def write(self, mode: Literal["w", "a"] = "w") -> None:
        """設定ファイルを書き込む

        Args:
            mode (Literal["w", "a"]): ファイルのモード

        Returns:
            None

        Examples:
            >>> config = BaseConfigArgs(filepath=Path("test.ini"), logger=logging.getLogger())
            >>> config.set_value(section="test", option="test", value="test")
            >>> config.write()

        Notes:
            modeが"w"の場合は、ファイルを上書きする
            modeが"a"の場合は、ファイルに追記する
        """
        with self.filepath.open(mode, encoding="utf-8") as fp:
            self._config.write(fp)
