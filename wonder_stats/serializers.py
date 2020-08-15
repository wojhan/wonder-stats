from django.contrib import auth
from rest_framework import serializers

from wonder_stats.models import Game, Point


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="profile.avatar", use_url=True)
    class Meta:
        model = auth.get_user_model()
        fields = ['id', 'username', 'avatar']


class GameSerializer(serializers.ModelSerializer):
    players = UserSerializer(many=True)
    class Meta:
        model = Game
        fields = ['id', 'created_at', 'finished_at', 'players']


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['type', 'game', 'player', 'value']
