from asgiref.sync import async_to_sync
import channels.layers
from django.db.models.signals import m2m_changed, post_save


from wonder_stats.serializers import GameSerializer
from wonder_stats.serializers import Game, Point
from wonder_stats.utils import MessageType


def players_changed(sender, instance, action, **kwargs):
    game = Game.objects.filter(finished_at=None).order_by('-created_at').first()
    serializer = GameSerializer(game).data
    if action == "post_add" or action == "post_remove" and game == instance:
        async_to_sync(channels.layers.get_channel_layer().group_send)(
            "lobby",
            {
                "type": "game_info_message",
                "message_type": MessageType.GAME_INFO,
                "game": serializer
            }
        )

def game_saved(sender, instance: Game, **kwargs):
    game = Game.objects.filter(finished_at=None).order_by('-created_at').first()
    if instance == game:
        serializer = GameSerializer(instance).data
        async_to_sync(channels.layers.get_channel_layer().group_send)(
            "lobby",
            {
                "type": "game_info_message",
                "message_type": MessageType.GAME_INFO,
                "game": serializer
            }
        )

        print(instance.finished_at)
    if instance.finished_at:
        print("Finished")
        async_to_sync(channels.layers.get_channel_layer().group_send)(
            f"game_{instance.id}",
            {
                "type": "game_info_message",
                "message_type": MessageType.FINISH_GAME,
            }
        )


def points_saved(sender, instance: Point, **kwargs):
    async_to_sync(channels.layers.get_channel_layer().group_send)(
        f"game_{instance.game_id}",
        {
            "type": "points_update_message",
            "message_type": MessageType.POINT_UPDATE,
            "player": instance.player_id,
            "point_type": instance.type,
            "value": instance.value
        }
    )


m2m_changed.connect(players_changed, sender=Game.players.through)
post_save.connect(points_saved, sender=Point)
post_save.connect(game_saved, sender=Game)