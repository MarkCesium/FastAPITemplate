class AppError(Exception):
    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message)
