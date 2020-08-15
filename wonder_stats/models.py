from django.contrib import auth
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(auth.get_user_model(), on_delete=models.CASCADE)
    avatar = models.ImageField()


class Game(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    players = models.ManyToManyField(auth.get_user_model(), related_name="games", null=True, blank=True)


class Point(models.Model):
    types = [
        ("MILITARY", 1),
        ("COINS", 2),
        ("WONDERS", 3),
        ("CULTURE", 4),
        ("TRADE", 5),
        ("GUILD", 6),
        ("SCIENCE", 7),
        ("CITIES", 8),
        ("LEADERS", 9)
    ]
    player = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name="points")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="+")
    type = models.IntegerField(choices=types)
    value = models.IntegerField()

