from django.apps import AppConfig


class WonderStatsConfig(AppConfig):
    name = 'wonder_stats'

    def ready(self):
        import wonder_stats.signals
