# Generated by Django 5.0.6 on 2024-07-07 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0015_match_deck'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='board_map',
            field=models.CharField(blank=True, choices=[('autumn', 'Autumn'), ('winter', 'Winter'), ('mountain', 'Mountain'), ('lake', 'Lake')], max_length=20, verbose_name='Map'),
        ),
    ]
