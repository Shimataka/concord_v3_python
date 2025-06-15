class DiscordSendLogError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Failed to import module: {self.message}"

    def __repr__(self) -> str:
        return f"ImportModuleError(message={self.message})"
