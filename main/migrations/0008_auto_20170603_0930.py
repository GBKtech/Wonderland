# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-03 08:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20170603_0853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Comment'),
        ),
        migrations.AlterField(
            model_name='like',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Post'),
        ),
    ]
