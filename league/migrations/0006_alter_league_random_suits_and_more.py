# Generated by Django 5.0.6 on 2024-08-02 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0005_league_board_map_league_deck_league_game_setup_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='random_suits',
            field=models.BooleanField(blank=True, null=True, verbose_name='random suits'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='random_suits',
            field=models.BooleanField(blank=True, null=True, verbose_name='random suits'),
        ),
    ]
