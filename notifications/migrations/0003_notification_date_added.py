# Generated by Django 4.0.1 on 2022-02-23 21:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_remove_notification_category_notification_action_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='date_added',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
