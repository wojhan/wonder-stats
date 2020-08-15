from django.urls import re_path

from wonder_stats import consumers

websocket_urlpatterns = [
    re_path(r'ws/game-lobby/$', consumers.LobbyConsumer),
    re_path(r'ws/game/(?P<id>\d+)/$', consumers.GameConsumer)
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
]