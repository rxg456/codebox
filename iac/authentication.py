from django.conf import settings
from django.utils import timezone
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from .models import Authorization


class BearerTokenAuthentication(BaseAuthentication):
    prefix = "bearer"
    active_time = settings.TOKEN_ACTIVE_TIME

    def authenticate(self, request: Request):
        path = request.get_full_path()
        if path == "/api/iac/auth/login/":
            return None
        token: str = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None
        token = token.lower()
        if not token.startswith(self.prefix):
            return None
        token = token[len(self.prefix):].strip()
        try:
            authorization = Authorization.objects.filter(token=token, expired_at__gte=timezone.now()).get()
            if authorization.user.is_active:
                return authorization.user, token
        except Authorization.DoesNotExist:
            pass
        raise AuthenticationFailed("authentication failed")


class BearerTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = BearerTokenAuthentication
    name = 'BearerTokenAuthentication'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer'
        }
