import importlib
import inspect
from logging import Logger
from pathlib import Path
from typing import TypeVar, cast

from pyresults import Err, Ok, Result

from concord.exception.import_module import ImportModuleError
from concord.model.import_class import LoadedClass

TypeOfAny = TypeVar("TypeOfAny", bound=type)


def _process_class(
    obj: object,
    base_class: TypeOfAny | None,
    module_path: str,
    logger: Logger | None,
) -> tuple[str, TypeOfAny] | None:
    if not inspect.isclass(obj):
        return None
    if base_class is None or (issubclass(obj, base_class) and obj != base_class):
        if logger is not None:
            msg = f"Loaded {obj.__name__} from {module_path}"
            logger.info(msg)
        return (obj.__module__, cast("TypeOfAny", obj))
    return None


def _import_module(
    module_path: str,
    base_class: TypeOfAny | None = None,
    logger: Logger | None = None,
) -> Result[list[tuple[str, TypeOfAny]], str]:
    if logger is not None:
        msg = f"Import: {module_path}"
        logger.info(msg)
    try:
        module = importlib.import_module(module_path)
        classes: list[tuple[str, TypeOfAny]] = []
        for _, obj in inspect.getmembers(module):
            result = _process_class(obj, base_class, module_path, logger)
            if result is not None:
                classes.append(result)
                if logger is not None:
                    msg = f"classes: {classes}"
                    logger.info(msg)
        return Ok(classes)
    except Exception as e:
        msg = f"Error importing {module_path}: {e}"
        if logger is not None:
            logger.exception(msg)
        return Err(msg)


def import_classes_from_directory(
    directory_path: str,
    include_name: list[str] | None = None,
    base_class: TypeOfAny | None = None,
    logger: Logger | None = None,
) -> list[LoadedClass[TypeOfAny]]:
    """指定されたディレクトリ内から、include_name に指定されたクラス名の
    ファイルに含まれるクラスを動的にインポートする

    Args:
        directory_path (str): インポート対象のディレクトリパス
        include_name (list[str] | None): インポート対象のファイル名のリスト (Noneの場合は全てのファイルが対象)
        base_class (TypeOfAny | None): 特定の基底クラスのインスタンスのみを取得する場合に指定
        logger (Logger | None): ファイルやクラスをロードするログを出力するロガー

    Returns:
        インポートされたクラスのリスト (クラス名, クラスオブジェクト) のタプル
    """
    classes: list[LoadedClass[TypeOfAny]] = []
    directory = Path(directory_path)

    for file_path in directory.glob("*.py"):
        if include_name and file_path.name not in include_name:
            continue

        module_name = file_path.stem
        module_path = f"{directory.name}.{module_name}"

        result = _import_module(module_path, base_class, logger)
        if result.is_err():
            raise ImportModuleError(result.unwrap_err())

        module_classes: list[LoadedClass[TypeOfAny]] = []
        for name, cls in result.unwrap():
            module_classes.append(LoadedClass[TypeOfAny](name, cls))

        classes.extend(module_classes)

    return classes
