# Generated by Django 5.1.6 on 2025-06-23 14:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_alter_user_reasonban_alter_usermoderationlog_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='music',
            name='playlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='musics', to='home.playlist'),
        ),
    ]
