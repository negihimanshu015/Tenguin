from typing import Optional

class AppExceptions(Exception):
    default_mssg = "An error occurred."
    status_code = 500

    def __init__(self, message: Optional[str]=None, code:Optional[int]=None):
        super().__init__(message or self.default_mssg)
        self.message = message or self.default_mssg
        if code is not None:
            self.status_code = code

class DomainException(AppExceptions):
    default_mssg = "Domain exception occurred."
    status_code = 400

class ValidationExceptions(AppExceptions):
    default_mssg = "Invalid Input"
    status_code = 400

class NotFoundExceptions(AppExceptions):
    default_mssg = "Not Found."
    status_code = 404

class ConflictExceptions(AppExceptions):
    default_mssg = "Conflict has occurred."
    status_code = 409

class PermissionExceptions(AppExceptions):
    default_mssg = "Permission Denied."
    status_code = 403

class AuthExceptions(AppExceptions):
    default_mssg = "Authentication error."
    status_code = 401

class RateLimitExceptions(AppExceptions):
    default_mssg = "Rate limit exceeded."
    status_code = 429