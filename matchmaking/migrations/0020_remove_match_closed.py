# Generated by Django 5.0.6 on 2024-07-13 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0019_alter_match_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='closed',
        ),
    ]