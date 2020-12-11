from django.apps import AppConfig


class HabitsConfig(AppConfig):
    name = 'habits'

    def ready(self):
        import habits.signals