# Generated by Django 5.1.1 on 2024-09-21 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_authtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authtoken',
            name='access_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='authtoken',
            name='token_acquired_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='authtoken',
            name='token_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]