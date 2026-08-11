from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/state/(?P<worker_id>[^/]+)/$', consumers.WorkerStateConsumer.as_asgi()),
    re_path(r'ws/vote/(?P<room_id>[^/]+)/$', consumers.VoteConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]
