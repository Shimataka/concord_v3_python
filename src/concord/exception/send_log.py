class DiscordSendLogError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
    def __str__(self) -> str:
        return f"Failed to send log to Discord: {self.message}"

    def __repr__(self) -> str:
        return f"DiscordSendLogError(message={self.message!r})"
