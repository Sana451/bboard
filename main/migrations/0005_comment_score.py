# Generated by Django 4.2.6 on 2023-11-01 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_advuser_send_messages_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='score',
            field=models.SmallIntegerField(choices=[(5, 'Топчик'), (4, 'Гуд'), (3, 'Пойдёт'), (2, 'Ни о чём'), (1, 'Оставь себе')], default=5, verbose_name='Оценка'),
            preserve_default=False,
        ),
    ]
