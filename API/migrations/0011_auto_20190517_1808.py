# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-05-17 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0010_auto_20190517_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='configs',
            name='cafeBazarCode',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='cafeBazarPaymentId',
            field=models.CharField(default=None, max_length=100, null=True, unique=True),
        ),
    ]
