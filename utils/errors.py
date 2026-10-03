class AppError(Exception):
    """Expected, user-facing error (bad input, unreadable PDF...)."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
