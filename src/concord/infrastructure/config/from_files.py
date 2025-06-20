import logging
import re
from pathlib import Path
from typing import Literal

from concord.model.config import BaseConfigArgs

DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "configs"
DEFAULT_CHANNEL_LIST_SECTION_NAME = "Discord.Channel"
DEFAULT_CHANNELS = Literal["dev_channel", "log_channel"]


class ConfigAPI(BaseConfigArgs):
    """API設定ファイルの読み込みを行うクラス

    API.iniが `src/concord/configs/API.ini` にあることを前提とする

    """

    def __init__(
        self,
        *,
        logger: logging.Logger,
        filepath: Path | None = None,
    ) -> None:
        if filepath is None:
            filepath = DEFAULT_CONFIG_DIR / "API.ini"
        super().__init__(filepath=filepath, logger=logger)

    def get_api_token(self, developer: str, key: str) -> str:
        """APIトークンを取得する

        Args:
            developer (str): 開発者名
            key (str): キー

        Returns:
            str: APIトークン
        """
        return self.get(section=developer, option=key)


class ConfigBOT(BaseConfigArgs):
    """BOT設定ファイルの読み込みを行うクラス

    - {BOT}.iniが `src/concord/configs/{BOT}.ini` にあることを前提とする
    - {BOT}はBOTの名前である

    """

    def __init__(
        self,
        *,
        bot_name: str,
        logger: logging.Logger,
        filepath: Path | None = None,
    ) -> None:
        if filepath is None:
            filepath = DEFAULT_CONFIG_DIR / f"{bot_name}.ini"
        super().__init__(filepath=filepath, logger=logger)
        self._channel_list_section_name = DEFAULT_CHANNEL_LIST_SECTION_NAME

    @property
    def name(self) -> str:
        """BOTの名前を取得する

        Returns:
            str: BOTの名前
        """
        return self.get(section="Discord.Bot", option="name")

    @name.setter
    def name(self, value: str) -> None:  # noqa: ARG002
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    @property
    def description(self) -> str:
        """BOTの説明を取得する

        Returns:
            str: BOTの説明
        """
        return self.get(section="Discord.Bot", option="description")

    @description.setter
    def description(self, value: str) -> None:  # noqa: ARG002
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    @property
    def channel_list_section_name(self) -> str:
        """チャンネルリストのセクション名を取得する

        Returns:
            str: チャンネルリストのセクション名
        """
        return self._channel_list_section_name

    @channel_list_section_name.setter
    def channel_list_section_name(self, value: str) -> None:
        if self._config.has_section(value):
            self._channel_list_section_name = value
        else:
            msg = f"Section {value} was not found in {self.filepath.absolute().as_posix()}"
            self._logger.error(msg)
            raise KeyError(msg)

    @property
    def discord_token(self) -> str:
        """Discordのトークンを取得する

        Returns:
            str: Discordのトークン
        """
        return self.get(section="Discord.API", option="token")

    @discord_token.setter
    def discord_token(self, value: None) -> None:  # noqa: ARG002
        msg = "Unexpected access"
        self._logger.error(msg)
        raise NameError(msg)

    @property
    def tool_exclusion(self) -> list[str]:
        """ツールの除外リストを取得する

        Returns:
            list[str]: ツールの除外リスト
        """

        def convert_str_to_list(arg: str) -> list[str]:
            """空白かピリオドで分割された文字列をlist[str]に変換する

            Args:
                arg (str): 変換するstr

            Returns:
                list[str]: 変換されたlist[str]
            """
            parsed_arg: list[str] = [s for s in re.split(r"\W", arg.strip("[").strip("]").strip()) if len(s) != 0]
            return parsed_arg

        try:
            exclusions = self.get(section="Discord.Tool", option="exclusions")
        except KeyError:
            msg = "Not found: section 'Discord.Task' or property 'exclusions'"
            self._logger.exception(msg)
            return []
        tool_exclusion = convert_str_to_list(exclusions)
        msg = f"Excluded tools: [{', '.join(tool_exclusion)}]"
        self._logger.info(msg)
        return tool_exclusion

    @tool_exclusion.setter
    def tool_exclusion(self, value: list[str]) -> None:  # noqa: ARG002
        msg = "Unexpected access"
        raise NameError(msg)

    def get_default_channel_id(self, name: DEFAULT_CHANNELS) -> int:
        """デフォルトチャンネルのIDを取得する

        Args:
            name (DEFAULT_CHANNELS = Literal["dev_channel", "log_channel"]): チャンネル名

        Returns:
            int: デフォルトチャンネルのID
        """
        try:
            return int(self.get(section="Discord.DefaultChannel", option=name))
        except KeyError:
            msg = f"Not found option '{name}' in the section 'Discord.DefaultChannel'"
            self._logger.exception(msg)
            raise

    def get_channel_to_id_mapping(
        self,
        *,
        section: str | None = None,
    ) -> dict[str, int]:
        """設定ファイルに記載された対応関係から、チャンネル名からチャンネルIDを取得する

        Args:
            section (str | None): セクション名

        Returns:
            dict[str, int]: チャンネル名からチャンネルIDのマッピング
        """
        if section is None:
            section = self.channel_list_section_name
        value = None
        _mapping: dict[str, int] = {}
        if self._config.has_section(section):
            for option in self._config.options(section):
                try:
                    value = self._config[section][option]
                    _mapping[option] = int(value)
                except ValueError:
                    msg = f"Invalid values to convert option {option} to int: {value}"
                    self._logger.exception(msg)
        else:
            msg = "[warning] No discord channel can read."
            self._logger.warning(msg)
        return _mapping

    def get_id_to_channel_mapping(
        self,
        *,
        section: str | None = None,
    ) -> dict[int, str]:
        """設定ファイルに記載された対応関係から、チャンネルIDからチャンネル名を取得する

        Args:
            section (str | None): セクション名

        Returns:
            dict[int, str]: チャンネルIDからチャンネル名のマッピング
        """
        if section is None:
            section = self.channel_list_section_name
        value = None
        _mapping: dict[int, str] = {}
        if self._config.has_section(section):
            for option in self._config.options(section):
                try:
                    value = self._config[section][option]
                    _mapping[int(value)] = option
                except ValueError:
                    msg = f"Invalid values to convert option {option} to int: {value}"
                    self._logger.exception(msg)
        else:
            msg = "[warning] No discord channel can read."
            self._logger.warning(msg)
        return _mapping


class ConfigArgs:
    """設定ファイルを読み込むクラス

    Args:
        bot_name (str): BOTの名前
        logger (logging.Logger): ロガー
        config_dir (Path | None): 設定ファイルのディレクトリパス
    """

    def __init__(
        self,
        *,
        bot_name: str,
        logger: logging.Logger,
        config_dir: Path | None = None,
    ) -> None:
        api_filepath = config_dir / "API.ini" if config_dir is not None else None
        bot_filepath = config_dir / f"{bot_name}.ini" if config_dir is not None else None
        self._logger = logger
        self.api = ConfigAPI(
            logger=self._logger,
            filepath=api_filepath,
        )
        self.bot = ConfigBOT(
            bot_name=bot_name,
            logger=self._logger,
            filepath=bot_filepath,
        )

    def load_config_from(self, *, file_stem: str) -> BaseConfigArgs:
        """設定ファイルを読み込む

        Args:
            file_stem (str): 設定ファイルの名前

        Returns:
            BaseConfigArgs: 設定ファイル
        """
        return BaseConfigArgs(
            filepath=DEFAULT_CONFIG_DIR / f"{file_stem}.ini",
            logger=self._logger,
        )
