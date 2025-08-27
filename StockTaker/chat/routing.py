from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<uuid:conversation_id>", consumers.ChatConsumer.as_asgi()),
]
