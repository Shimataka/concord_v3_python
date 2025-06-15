"""Tests for dynamic import system."""

# mypy: ignore-errors

from typing import TYPE_CHECKING
from unittest import mock

# import pytest
# from src.concord.src.core.exceptions.import_module import ImportModuleError
from concord.infrastructure.discord.dynamic_import import (
    _import_module,  # type: ignore[reportPrivateUsage]
    _process_class,  # type: ignore[reportPrivateUsage]
    import_classes_from_directory,
)

if TYPE_CHECKING:
    from discord.ext.commands import Cog

    from concord.model.import_class import LoadedClass


class MockBaseClass:
    """Mock base class for testing."""


class MockChildClass(MockBaseClass):
    """Mock child class for testing."""


class MockUnrelatedClass:
    """Mock unrelated class for testing."""


class TestProcessClass:
    """Test the _process_class function."""

    def test_process_class_with_valid_class(self) -> None:
        """Test processing a valid class that inherits from base class."""
        mock_logger = mock.Mock()

        result = _process_class(
            MockChildClass,
            MockBaseClass,
            "test.module",
            mock_logger,
        )

        assert result is not None
        assert result[0] == MockChildClass.__module__
        assert result[1] == MockChildClass
        mock_logger.info.assert_called_once()

    def test_process_class_with_base_class_itself(self) -> None:
        """Test that base class itself is excluded."""
        result = _process_class(
            MockBaseClass,
            MockBaseClass,
            "test.module",
            None,
        )

        assert result is None

    def test_process_class_with_unrelated_class(self) -> None:
        """Test processing a class that doesn't inherit from base class."""
        result = _process_class(
            MockUnrelatedClass,
            MockBaseClass,
            "test.module",
            None,
        )

        assert result is None

    def test_process_class_with_no_base_class(self) -> None:
        """Test processing class when no base class is specified."""
        mock_logger = mock.Mock()

        result = _process_class(  # type: ignore[reportUnknownVariableType]
            MockChildClass,
            None,
            "test.module",
            mock_logger,
        )

        assert result is not None
        assert result[0] == MockChildClass.__module__
        assert result[1] == MockChildClass

    def test_process_class_with_non_class_object(self) -> None:
        """Test processing a non-class object."""
        result = _process_class(
            "not_a_class",  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
            MockBaseClass,
            "test.module",
            None,
        )

        assert result is None

    def test_process_class_with_logger_none(self) -> None:
        """Test that function works when logger is None."""
        result = _process_class(
            MockChildClass,
            MockBaseClass,
            "test.module",
            None,
        )

        assert result is not None


class TestImportModule:
    """Test the _import_module function."""

    @mock.patch("concord.infrastructure.discord.dynamic_import.importlib.import_module")
    @mock.patch("concord.infrastructure.discord.dynamic_import.inspect.getmembers")
    def test_import_module_success(
        self,
        mock_getmembers: mock.Mock,
        mock_import_module: mock.Mock,
    ) -> None:
        """Test successful module import."""
        mock_module = mock.Mock()
        mock_import_module.return_value = mock_module
        mock_getmembers.return_value = [
            ("MockChildClass", MockChildClass),
            ("MockUnrelatedClass", MockUnrelatedClass),
        ]

        mock_logger = mock.Mock()
        result = _import_module("test.module", MockBaseClass, mock_logger)

        assert result.is_ok()
        classes = result.unwrap()
        assert len(classes) == 1
        assert classes[0][1] == MockChildClass
        mock_logger.info.assert_called()

    @mock.patch("concord.infrastructure.discord.dynamic_import.importlib.import_module")
    def test_import_module_failure(self, mock_import_module: mock.Mock) -> None:
        """Test module import failure."""
        mock_import_module.side_effect = ImportError("Module not found")

        result = _import_module("nonexistent.module")  # type: ignore[reportUnknownVariableType]

        assert result.is_err()
        error_msg = result.unwrap_err()
        assert "Error importing nonexistent.module" in error_msg
        assert "Module not found" in error_msg

    @mock.patch("concord.infrastructure.discord.dynamic_import.importlib.import_module")
    @mock.patch("concord.infrastructure.discord.dynamic_import.inspect.getmembers")
    def test_import_module_no_base_class(
        self,
        mock_getmembers: mock.Mock,
        mock_import_module: mock.Mock,
    ) -> None:
        """Test module import without base class filter."""
        mock_module = mock.Mock()
        mock_import_module.return_value = mock_module
        mock_getmembers.return_value = [
            ("MockChildClass", MockChildClass),
            ("MockUnrelatedClass", MockUnrelatedClass),
        ]

        result = _import_module("test.module", None, None)  # type: ignore[reportUnknownVariableType]

        assert result.is_ok()
        classes = result.unwrap()  # type: ignore[reportUnknownVariableType]
        assert len(classes) == 2  # type: ignore[reportUnknownVariableType]


class TestImportClassesFromDirectory:
    """Test the import_classes_from_directory function."""

    @mock.patch("concord.infrastructure.discord.dynamic_import.Path")
    @mock.patch("concord.infrastructure.discord.dynamic_import._import_module")
    def test_import_classes_from_directory_success(
        self,
        mock_import_module: mock.Mock,
        mock_path: mock.Mock,
    ) -> None:
        """Test successful directory import."""
        # Setup mocks
        mock_file1 = mock.Mock()
        mock_file1.name = "test1.py"
        mock_file1.stem = "test1"

        mock_file2 = mock.Mock()
        mock_file2.name = "test2.py"
        mock_file2.stem = "test2"

        mock_directory = mock.Mock()
        mock_directory.name = "test_dir"
        mock_directory.glob.return_value = [mock_file1, mock_file2]

        mock_path.return_value = mock_directory

        # Mock successful imports
        from pyresults import Ok

        mock_import_module.side_effect = [
            Ok([("test1", MockChildClass)]),
            Ok([("test2", MockChildClass)]),
        ]

        mock_logger = mock.Mock()
        result = import_classes_from_directory(  # type: ignore[reportUnknownVariableType]
            "/test/path",
            None,
            MockBaseClass,  # type: ignore[reportArgumentType]
            mock_logger,
        )

        assert len(result) == 2  # type: ignore[reportUnknownVariableType]
        assert all(loaded_class.class_type == MockChildClass for loaded_class in result)  # type: ignore[reportUnknownVariableType]

    @mock.patch("concord.infrastructure.discord.dynamic_import.Path")
    @mock.patch("concord.infrastructure.discord.dynamic_import._import_module")
    def test_import_classes_with_include_name_filter(
        self,
        mock_import_module: mock.Mock,
        mock_path: mock.Mock,
    ) -> None:
        """Test directory import with include_name filter."""
        mock_file1 = mock.Mock()
        mock_file1.name = "included.py"
        mock_file1.stem = "included"

        mock_file2 = mock.Mock()
        mock_file2.name = "excluded.py"
        mock_file2.stem = "excluded"

        mock_directory = mock.Mock()
        mock_directory.name = "test_dir"
        mock_directory.glob.return_value = [mock_file1, mock_file2]

        mock_path.return_value = mock_directory

        from pyresults import Ok

        mock_import_module.return_value = Ok([("included", MockChildClass)])

        result = import_classes_from_directory(  # type: ignore[reportUnknownVariableType]
            "/test/path",
            ["included.py"],
            MockBaseClass,  # type: ignore[reportArgumentType]
            None,
        )

        assert len(result) == 1  # type: ignore[reportUnknownVariableType]
        assert mock_import_module.call_count == 1

    # @mock.patch("src.concord.src.core.utils.dynamic_import.Path")
    # @mock.patch("src.concord.src.core.utils.dynamic_import._import_module")
    # def test_import_classes_import_error(
    #     self,
    #     mock_import_module: mock.Mock,
    #     mock_path: mock.Mock,
    # ) -> None:
    #     """Test directory import with import error."""
    #     mock_file = mock.Mock()
    #     mock_file.name = "test.py"
    #     mock_file.stem = "test"
    #
    #     mock_directory = mock.Mock()
    #     mock_directory.name = "test_dir"
    #     mock_directory.glob.return_value = [mock_file]
    #
    #     mock_path.return_value = mock_directory
    #
    #     from pyresults import Err
    #
    #     mock_import_module.return_value = Err("Import failed")
    #
    #     with pytest.raises(ImportModuleError) as exc_info:
    #         import_classes_from_directory("/test/path")  # type: ignore[reportPrivateUsage]
    #
    #     assert "Import failed" in str(exc_info.value)

    @mock.patch("concord.infrastructure.discord.dynamic_import.Path")
    def test_import_classes_empty_directory(self, mock_path: mock.Mock) -> None:
        """Test directory import with empty directory."""
        mock_directory = mock.Mock()
        mock_directory.name = "empty_dir"
        mock_directory.glob.return_value = []

        mock_path.return_value = mock_directory

        result: list[LoadedClass[type[Cog]]] = import_classes_from_directory("/test/path")

        assert result == []

    @mock.patch("concord.infrastructure.discord.dynamic_import.Path")
    @mock.patch("concord.infrastructure.discord.dynamic_import._import_module")
    def test_import_classes_no_base_class(
        self,
        mock_import_module: mock.Mock,
        mock_path: mock.Mock,
    ) -> None:
        """Test directory import without base class filter."""
        mock_file = mock.Mock()
        mock_file.name = "test.py"
        mock_file.stem = "test"

        mock_directory = mock.Mock()
        mock_directory.name = "test_dir"
        mock_directory.glob.return_value = [mock_file]

        mock_path.return_value = mock_directory

        from pyresults import Ok

        mock_import_module.return_value = Ok(
            [
                ("test", MockChildClass),
                ("test", MockUnrelatedClass),
            ],
        )

        result: list[LoadedClass[type[Cog]]] = import_classes_from_directory(
            "/test/path",
            None,
            None,
            None,
        )  # type: ignore[reportPrivateUsage]

        assert len(result) == 2  # type: ignore[reportPrivateUsage]
