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

    def __init__(
        self,
        filepath: Path | None,
        logger: logging.Logger,
        *,
        is_required: bool = False,
    ) -> None:
        self._filepath = filepath
        self._config: ConfigParser | None = None
        self._logger = logger
        if is_required:
            self._check_existence()

    @property
    def filepath(self) -> Path:
        if self._filepath is None:
            msg = "Error: filepath is not set"
            self._logger.error(msg)
            raise ValueError(msg)
        return self._filepath.resolve()

    @property
    def config(self) -> ConfigParser:
        if self._config is None:
            self._config = ConfigParser()
            self._read()
        return self._config

    def _check_existence(self) -> None:
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

    def _read(self) -> None:
        if self._config is None:
            msg = "Error: config is not initialized"
            self._logger.exception(msg)
            raise ValueError(msg)
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
        if self.config.has_section(
            section=section,
        ) and self.config.has_option(
            section=section,
            option=option,
        ):
            return self.config[section][option]
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
        if self.config.has_section(section):
            self.config[section][option] = value
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
            self.config.write(fp)
