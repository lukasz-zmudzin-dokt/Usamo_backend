from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from chat.consumers import ChatConsumer
from notification.consumers import NotificationConsumer
from notification.token_auth import TokenAuthMiddleware
application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(
                [
                    # url(r"^chat/(?P<username>[\w.@+-]+)/$", ChatConsumer),
                    url("notification/count/unread", NotificationConsumer)
                ]
            )
        )
    )
})