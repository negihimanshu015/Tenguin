from rest_framework.throttling import UserRateThrottle


class AuthenticatedUserThrottle(UserRateThrottle):
    scope = "authenticated_user"
