# Generated by Django 4.0.1 on 2022-01-25 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='date_updated',
            field=models.DateTimeField(null=True),
        ),
    ]