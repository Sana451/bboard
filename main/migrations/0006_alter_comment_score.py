# Generated by Django 4.2.6 on 2023-11-15 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_comment_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='score',
            field=models.SmallIntegerField(choices=[(None, 'Оцените товар'), (5, 'Топчик (5)'), (4, 'Гуд (4)'), (3, 'Пойдёт (3)'), (2, 'Ни о чём (2)'), (1, 'Оставь себе (1)')], default=5, verbose_name='Оценка'),
        ),
    ]
