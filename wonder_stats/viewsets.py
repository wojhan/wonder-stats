from django.contrib import auth
from rest_framework import viewsets

from wonder_stats import models, serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = auth.get_user_model().objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = models.Game.objects.filter(finished_at=None).order_by('-created_at')[:1]
    serializer_class = serializers.GameSerializer