# Generated by Django 5.1.1 on 2024-09-25 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='clock_end',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='move',
            name='clock_start',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='move',
            name='time_spent',
            field=models.FloatField(blank=True, null=True),
        ),
    ]