# Generated by Django 4.0.1 on 2022-02-20 16:32

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='myuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='myuser',
            name='password',
            field=models.CharField(default='default', max_length=128, verbose_name='password'),
            preserve_default=False,
        ),
    ]
