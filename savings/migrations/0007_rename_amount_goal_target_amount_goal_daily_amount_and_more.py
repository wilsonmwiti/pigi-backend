# Generated by Django 4.0.1 on 2022-02-14 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0006_alter_lockedsavings_duration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goal',
            old_name='amount',
            new_name='target_amount',
        ),
        migrations.AddField(
            model_name='goal',
            name='daily_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='goal',
            name='maturity_date',
            field=models.DateTimeField(verbose_name='maturity_date'),
        ),
    ]
