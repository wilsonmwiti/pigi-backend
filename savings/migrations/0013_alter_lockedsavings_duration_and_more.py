# Generated by Django 4.0.1 on 2022-02-21 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0012_alter_goal_thumbnail_alter_lockedsavings_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockedsavings',
            name='duration',
            field=models.IntegerField(choices=[(3, 'Quarterly'), (6, 'Semi Anually'), (9, '9 months'), (12, 'Anually')]),
        ),
        migrations.AlterField(
            model_name='lockedsavings',
            name='thumbnail',
            field=models.ImageField(default='goals/pigibank-default.jpg', null=True, upload_to='locked_savings'),
        ),
    ]
