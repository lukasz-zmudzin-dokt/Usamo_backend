from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat.consumers import ChatConsumer, InboxConsumer
from notification.consumers import NotificationConsumer
from notification.token_auth import TokenAuthMiddlewareStack


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                [
                    url(r"^chat/(?P<username>\S+)/$", ChatConsumer),
                    # url("chat/", InboxConsumer),
                    url("notification/ws", NotificationConsumer)
                ]
            )
        )
    )
})