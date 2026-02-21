import json

import jwt
import requests
from core.services import user_services
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

JWKS_CACHE_KEY = "clerk_jwks"
JWKS_CACHE_TTL = 60 * 60

def _jwks_url(issuer: str) -> str:
    return issuer.rstrip("/") + "/.well-known/jwks.json"

def _get_jwks(issuer: str):
    jwks = cache.get(JWKS_CACHE_KEY)

    if jwks:
        return jwks

    response = requests.get(_jwks_url(issuer), timeout=10)
    response.raise_for_status()
    jwks = response.json()

    cache.set(JWKS_CACHE_KEY, jwks, JWKS_CACHE_TTL)
    return jwks

def _get_public_key(token:str, issuer:str):
    unverified = jwt.get_unverified_header(token)
    kid = unverified.get("kid")
    if not kid:
        raise AuthenticationFailed("Invalid header token")

    jwks = _get_jwks(issuer)

    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    cache.delete(JWKS_CACHE_KEY)
    jwks = _get_jwks(issuer)

    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    raise AuthenticationFailed("Sighning key invalid")

class ClerkAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")

        if not header:
            return None
        parts = header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        issuer = settings.CLERK_ISSUER
        audience = getattr(settings, "CLERK_AUDIENCE", None)

        try:
            public_key = _get_public_key(token, issuer)

            token_args = {
                "key": public_key,
                "algorithms": ["RS256"],
                "issuer": issuer,
                "options": {"require": ["exp", "iat", "sub"]}
            }

            if audience:
                token_args["audience"] = audience

            payload = jwt.decode(token, **token_args)

        except Exception as e:
            raise AuthenticationFailed(str(e)) from e

        clerk_id = payload.get("sub")

        if not clerk_id:
            raise AuthenticationFailed("Failed to get clerk id")

        User = get_user_model()

        try:
            user = User.objects.get(clerk_id = clerk_id)

        except User.DoesNotExist:
            user = self._auto_create_user(User, clerk_id, payload)

        return (user, token)


    def _auto_create_user(self, User, clerk_id, payload):
        try:
            return user_services.create_user(clerk_id=clerk_id, payload=payload)

        except Exception as e:
            raise AuthenticationFailed(str(e)) from e





