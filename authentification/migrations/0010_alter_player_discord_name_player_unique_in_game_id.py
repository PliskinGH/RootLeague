# Generated by Django 5.1.1 on 2024-12-01 19:17

import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('authentification', '0009_alter_player_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='discord_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='discord username'),
        ),
        migrations.AddConstraint(
            model_name='player',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('in_game_name'), models.F('in_game_id'), name='unique_in_game_id'),
        ),
    ]
