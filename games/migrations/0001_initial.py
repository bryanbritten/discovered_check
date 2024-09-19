# Generated by Django 5.1.1 on 2024-09-19 18:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('game_id', models.CharField(max_length=8)),
                ('rated', models.BooleanField()),
                ('variant', models.CharField(max_length=255)),
                ('speed', models.CharField(choices=[('blitz', 'Blitz'), ('bullet', 'Bullet'), ('ultrabullet', 'Ultra Bullet'), ('classical', 'Classical'), ('correspondence', 'Correspondence'), ('rapid', 'Rapid')], max_length=20)),
                ('perf', models.CharField(choices=[('blitz', 'Blitz'), ('bullet', 'Bullet'), ('ultrabullet', 'Ultra Bullet'), ('classical', 'Classical'), ('correspondence', 'Correspondence'), ('rapid', 'Rapid'), ('chess960', 'Chess960'), ('crazyhouse', 'Crazyhouse'), ('antichess', 'Antichess'), ('atomic', 'Atomic'), ('horde', 'Horde'), ('kingOfTheHill', 'King of the Hill'), ('racingKings', 'Racing Kings'), ('threeCheck', 'Three-check')], max_length=20)),
                ('status', models.CharField(max_length=255)),
                ('white_player', models.CharField(max_length=255)),
                ('white_rating_before', models.SmallIntegerField()),
                ('white_rating_after', models.SmallIntegerField()),
                ('black_player', models.CharField(max_length=255)),
                ('black_rating_before', models.SmallIntegerField()),
                ('black_rating_after', models.SmallIntegerField()),
                ('winner', models.CharField(choices=[('black', 'Black'), ('white', 'White')], max_length=5)),
                ('created_at', models.DateTimeField()),
                ('lastMoveAt', models.DateTimeField()),
                ('initial_clock', models.SmallIntegerField()),
                ('increment', models.SmallIntegerField()),
                ('total_time', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Opening',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eco', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=255)),
                ('notation', models.CharField(max_length=255)),
                ('ply', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('move_number', models.SmallIntegerField()),
                ('move_notation', models.CharField(max_length=10)),
                ('color', models.CharField(choices=[('black', 'Black'), ('white', 'White')], max_length=5)),
                ('clock_start', models.SmallIntegerField()),
                ('clock_end', models.SmallIntegerField()),
                ('time_spent', models.SmallIntegerField()),
                ('game_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.game')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='opening_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.opening'),
        ),
    ]