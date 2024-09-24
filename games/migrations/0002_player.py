# Generated by Django 5.1.1 on 2024-09-24 18:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('lichess', 'Lichess'), ('chesscom', 'Chess.com')], max_length=10)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('blitz_games', models.IntegerField(default=0)),
                ('blitz_rating', models.SmallIntegerField(default=0)),
                ('bullet_games', models.IntegerField(default=0)),
                ('bullet_rating', models.SmallIntegerField(default=0)),
                ('ultra_bullet_games', models.IntegerField(default=0)),
                ('ultra_bullet_rating', models.SmallIntegerField(default=0)),
                ('rapid_games', models.IntegerField(default=0)),
                ('rapid_rating', models.SmallIntegerField(default=0)),
                ('puzzles_completed', models.IntegerField(default=0)),
                ('puzzles_rating', models.SmallIntegerField(default=0)),
                ('classical_games', models.IntegerField(default=0)),
                ('classical_rating', models.SmallIntegerField(default=0)),
                ('member_since', models.DateTimeField(blank=True, null=True)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
                ('is_disabled', models.BooleanField(default=False)),
                ('violated_tos', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]