from typing import Optional


class AppException(Exception):
    default_mssg = "An error occurred."
    status_code = 500

    def __init__(self, message: Optional[str]=None, code:Optional[int]=None):
        super().__init__(message or self.default_mssg)
        self.message = message or self.default_mssg
        if code is not None:
            self.status_code = code

class DomainException(AppException):
    default_mssg = "Domain exception occurred."
    status_code = 400

class ValidationException(AppException):
    default_mssg = "Invalid Input"
    status_code = 400

class NotFoundException(AppException):
    default_mssg = "Not Found."
    status_code = 404

class ConflictException(AppException):
    default_mssg = "Conflict has occurred."
    status_code = 409

class PermissionException(AppException):
    default_mssg = "Permission Denied."
    status_code = 403

class AuthException(AppException):
    default_mssg = "Authentication error."
    status_code = 401

class RateLimitException(AppException):
    default_mssg = "Rate limit exceeded."
    status_code = 429
