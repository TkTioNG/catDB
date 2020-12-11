from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

EXPIRING_HOUR = 24


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication that will be expring within 24 hours.
    """

    # overwrite
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is inactive")

        if timezone.now() - token.created > timedelta(hours=settings.AUTH_TOKEN_EXPIRING_HOURS):
            raise AuthenticationFailed("Token has expired")

        return (token.user, token)
