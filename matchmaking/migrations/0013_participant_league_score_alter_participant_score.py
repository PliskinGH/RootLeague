# Generated by Django 5.0.6 on 2024-07-07 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0012_remove_participant_winner_alter_participant_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='league_score',
            field=models.DecimalField(blank=True, choices=[(1.0, 1), (0.5, 0.5), (0.0, 0)], decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
