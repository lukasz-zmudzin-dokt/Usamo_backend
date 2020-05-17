from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from rest_framework import HTTP_HEADER_ENCODING


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        if b'sec-websocket-protocol' in headers:
            try:
                token_key = headers[b'sec-websocket-protocol'].decode('utf-8')
                knoxAuth = TokenAuthentication()
                try:
                    user, auth_token = knoxAuth.authenticate_credentials(token_key.encode(HTTP_HEADER_ENCODING))
                except Exception:
                    return self.inner(scope)
                scope['user'] = user
            except AuthToken.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
