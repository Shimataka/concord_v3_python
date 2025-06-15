from pathlib import Path


class DirectoryNotFoundError(Exception):
    def __init__(self, path: Path, message: str | None = None) -> None:
        self.path = path
        if message is None:
            message = f"Directory not found: {path}"
        super().__init__(message)

    def __str__(self) -> str:
        return f"Directory not found: {self.path}"

    def __repr__(self) -> str:
        return f"DirectoryNotFoundError(path={self.path})"


class ImportModuleError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Failed to import module: {self.message}"

    def __repr__(self) -> str:
        return f"ImportModuleError(message={self.message})"
