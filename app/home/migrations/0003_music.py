# Generated by Django 4.2.3 on 2024-12-17 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_playlist_typeplaylist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fileName', models.CharField(max_length=63)),
                ('alternativeName', models.CharField(default=None, max_length=63)),
                ('file', models.FileField(upload_to='musics/')),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.playlist')),
            ],
        ),
    ]