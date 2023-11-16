from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Доска объявлений'

    def ready(self):
        """Привязка обработчиков:
         1. post_register_dispatcher к сигналу post_register
         2. post_register_dispatcher к сигналу post_register
         """
        from . import signals  # неявная привязка
        # как альтернатива (явная привязка)
        # request_finished.connect(post_register_dispatcher)
        # post_save.connect(post_save_dispatcher)
