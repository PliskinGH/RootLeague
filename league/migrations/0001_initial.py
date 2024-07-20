# Generated by Django 5.0.6 on 2024-07-20 22:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='name')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='start date')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='end date')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='name')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='start date')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='end date')),
                ('league', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seasons', to='league.league', verbose_name='league')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='league',
            name='active_season',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_in_league', to='league.tournament', verbose_name='active season'),
        ),
    ]
