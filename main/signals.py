from django.db.models.signals import post_save
from django.dispatch import receiver

from main.forms import RegisterForm
from main.models import AdvUser, Comment
from main.my_signals import post_register
from main.utilities import send_activation_notification, send_new_comment_notification


@receiver(post_register, sender=RegisterForm)
def post_register_dispatcher(sender, **kwargs):
    instance = kwargs['instance']
    print(instance)
    send_activation_notification(instance)  # RegisterForm в методе save отправляет: instance=user


@receiver(post_save, sender=Comment)
def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])
