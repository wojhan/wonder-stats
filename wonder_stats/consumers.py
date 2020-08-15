import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

import typing

import wonder_stats.models
import wonder_stats.serializers
from wonder_stats import utils


class WebSocketError:
    def __init__(self, error):
        self.error = error

    @property
    def json(self):
        return json.dumps({'type': 'error', 'error': self.error})


class WebSocketMessage:
    def __init__(self, message_type: utils.MessageType, **kwargs):
        self.type = message_type.value if isinstance(message_type, utils.MessageType) else message_type
        kwargs['message_type'] = self.type
        self.json = json.dumps(kwargs)

        for key, value in kwargs.items():
            setattr(self, str(key), value)


class Consumer(WebsocketConsumer):
    def __init__(self, room_group_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = room_group_name

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def send_to_client(self, message: WebSocketMessage):
        self.send(text_data=message.json)

    def send_error(self, error: str):
        err = WebSocketError(error).json
        self.send(text_data=err, close=True)

    def broadcast(self, message: WebSocketMessage):
        pass

    def game_info_message(self, event):
        event.pop('type')
        message = WebSocketMessage(**event)
        self.send_to_client(message)


class GameConsumer(Consumer):
    """
    Received messages:
        'player_joined_request':
            'player' - id of a player

        'player_left_request':
            'player' - id of a player

        'update_point_request':
            'player' - id of a player
            'point_type' - a point category stored in the database
            'value' - integer value of points

    Broadcasting messages:
        'player_joined':
            'game' - id of a game related to a join event
            'player' - id of a player who joined
        'player_left':
            'game' - id of a game related to a leave event
            'player' - id of a player who left
        'update_point':
            'game' - id of a game
            'player' - id of a player
            'point_type'
            'value'
        'finish_game':
            'game'


    """
    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.room_name = self.scope['url_route']['kwargs']['id']
        self.room_group_name = 'game_%s' % self.room_name
        self.game = None
        self.serialized_game = None

    def connect(self):
        super().connect()
        try:
            self.game: wonder_stats.models.Game = wonder_stats.models.Game.objects.get(pk=self.room_name)
            self.serialized_game = wonder_stats.serializers.GameSerializer(self.game).data
        except wonder_stats.models.Game.DoesNotExist:
            self.send_error(f'Game with id {self.room_name} does not exist')
        else:
            message = WebSocketMessage(utils.MessageType.GAME_INFO_RESPONSE, game=self.serialized_game)
            self.send_to_client(message)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        sender = text_data_json['sender'] if 'sender' in text_data_json else None

        if text_data_json['type'] == utils.MessageType.POINT_UPDATE_REQUEST.value:
            player = int(text_data_json['player'])
            point_type = int(text_data_json['point_type'])
            value = int(text_data_json['value'])
            wonder_stats.models.Point.objects.update_or_create(game=self.game, player_id=player, type=point_type, defaults={"value": value})

            if sender:
                message = WebSocketMessage(utils.MessageType.POINT_UPDATE_RESPONSE, point_type=point_type, value=value, sender=sender)
                self.send_to_client(message)

        if text_data_json['type'] == utils.MessageType.GET_POINTS_REQUEST.value:
            game = int(text_data_json['game'])
            player = int(text_data_json['player'])

            if game != self.game.id:
                self.send_error('Incorrect game id provided')

            points = wonder_stats.models.Point.objects.filter(game=self.game, player_id=player)
            points = wonder_stats.serializers.PointSerializer(points, many=True).data

            if sender:
                message = WebSocketMessage(utils.MessageType.GET_POINTS_RESPONSE, points=points, sender=sender)
                self.send_to_client(message)

        if text_data_json['type'] == utils.MessageType.FINISH_GAME_REQUEST.value:
            game = int(text_data_json['game'])
            if game != self.game.id:
                self.send_error('Incorrect game id provided')

            self.game.finished_at = datetime.now()
            self.game.save()

            if sender:
                message = WebSocketMessage(utils.MessageType.FINISH_GAME_RESPONSE, sender=sender)
                self.send_to_client(message)

    def points_update_message(self, event):
        event.pop('type')
        message = WebSocketMessage(**event)
        self.send_to_client(message)


class LobbyConsumer(Consumer):
    def __init__(self, *args, **kwargs):
        self.room_group_name = 'lobby'
        super().__init__(self.room_group_name, *args, **kwargs)

    def connect(self):
        super().connect()

        current_game: wonder_stats.models.Game = wonder_stats.models.Game.objects.filter(finished_at=None).last()
        serialized_game = wonder_stats.serializers.GameSerializer(current_game).data if current_game else None

        message = WebSocketMessage(utils.MessageType.GAME_INFO_RESPONSE, game=serialized_game)
        self.send_to_client(message)

    def __get_current_game(self) -> typing.Tuple[wonder_stats.models.Game, typing.Dict]:
        current_game: wonder_stats.models.Game = wonder_stats.models.Game.objects.filter(finished_at=None).last()
        serialized_game = wonder_stats.serializers.GameSerializer(current_game).data

        return current_game, serialized_game

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        sender = text_data_json['sender'] if 'sender' in text_data_json else None

        if text_data_json['type'] == utils.MessageType.GAME_INFO_REQUEST.value:
            serialized_game = self.__get_current_game()[1]
            if sender:
                message = WebSocketMessage(utils.MessageType.GAME_INFO_RESPONSE, game=serialized_game, sender=sender)
                self.send_to_client(message)

        if text_data_json['type'] == utils.MessageType.PLAYER_JOINED_REQUEST.value:
            game, serialized_game = self.__get_current_game()
            if game.id != text_data_json['game']:
                self.send_error('Modifying archived game is not allowed')
            try:
                user = User.objects.get(pk=int(text_data_json['player']))
            except User.DoesNotExist:
                self.send_error('Given user does not exist')

            game.players.add(user)
            serialized_game = wonder_stats.serializers.GameSerializer(game).data

            if sender:
                message = WebSocketMessage(utils.MessageType.PLAYER_JOINED_RESPONSE, game=serialized_game, sender=sender)
                self.send_to_client(message)

        if text_data_json['type'] == utils.MessageType.PLAYER_LEFT_REQUEST.value:
            game, serialized_game = self.__get_current_game()
            if game.id != text_data_json['game']:
                self.send_error('Modifying archived game is not allowed')
            try:
                user = User.objects.get(pk=int(text_data_json['player']))
            except User.DoesNotExist:
                self.send_error('Given user does not exist')

            game.players.remove(user)
            serialized_game = wonder_stats.serializers.GameSerializer(game).data

            if sender:
                message = WebSocketMessage(utils.MessageType.PLAYER_LEFT_RESPONSE, game=serialized_game, sender=sender)
                self.send_to_client(message)

        if text_data_json['type'] == utils.MessageType.CREATE_GAME_REQUEST.value:
            game = wonder_stats.models.Game.objects.create()

            if sender:
                message = WebSocketMessage(utils.MessageType.CREATE_GAME_RESPONSE, sender=sender)
                self.send_to_client(message)