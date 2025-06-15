from argparse import ArgumentParser
from pathlib import Path

from concord.exception.import_module import DirectoryNotFoundError
from concord.model.argument import Args


def on_launch() -> Args:
    parser = ArgumentParser()
    parser.add_argument(
        "--bot-name",
        type=str,
        required=True,
        help="BOTの名前を指定します。",
    )
    parser.add_argument(
        "--tool-directory-paths",
        type=str,
        required=False,
        default="",
        help="ツールのディレクトリパスを指定します。複数指定する場合はスペースで区切ります。",
    )
    parser.add_argument(
        "--is-debug",
        action="store_true",
        required=False,
        default=False,
        help="デバッグモードかどうかを指定します。",
    )
    args = parser.parse_args()

    # typing
    bot_name = args.bot_name
    if not isinstance(bot_name, str):
        msg = "Invalid arguments: bot_name must be a string"
        raise TypeError(msg)
    if isinstance(args.tool_directory_paths, str):
        resolved_and_validated_paths: list[Path] = []
        raw_paths = args.tool_directory_paths
        if len(raw_paths) != 0:
            for raw_path in raw_paths.split():
                path = Path(raw_path)
                path = path if path.is_absolute() else (Path.cwd() / path)
                path = path.resolve()
                if not path.is_dir() or not path.exists():
                    raise DirectoryNotFoundError(path)
                resolved_and_validated_paths.append(path)
        resolved_and_validated_paths = list(set(resolved_and_validated_paths))
    else:
        msg = "Invalid arguments: tool_directory_paths must be a string or list[Path]"
        raise TypeError(msg)
    is_debug = args.is_debug
    if not isinstance(is_debug, bool):
        msg = "Invalid arguments: is_debug must be a bool"
        raise TypeError(msg)

    return Args(
        bot_name=bot_name,
        tool_directory_paths=resolved_and_validated_paths,
        is_debug=is_debug,
    )
