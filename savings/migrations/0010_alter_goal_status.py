# Generated by Django 4.0.1 on 2022-02-16 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0009_alter_goal_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='status',
            field=models.IntegerField(choices=[(0, 'Good'), (1, 'Bad'), (2, 'Excellent')], default=0),
        ),
    ]