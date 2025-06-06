# Generated by Django 5.1.6 on 2025-03-24 13:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_rename_soundboarddim_userpreference_soundboarddim'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavoritePublicSoundboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to=settings.AUTH_USER_MODEL)),
                ('uuidSoundboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='home.soundboard')),
            ],
        ),
    ]
