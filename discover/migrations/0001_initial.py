# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-29 08:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meetup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latlong', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizer', models.CharField(max_length=200)),
                ('meetup_pt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discover.Meetup')),
            ],
        ),
        migrations.AddField(
            model_name='passenger',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discover.Trip'),
        ),
    ]
