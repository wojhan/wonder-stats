from django.contrib import admin

from wonder_stats import models

# Register your models here.
admin.site.register(models.Game)
admin.site.register(models.Point)
admin.site.register(models.Profile)