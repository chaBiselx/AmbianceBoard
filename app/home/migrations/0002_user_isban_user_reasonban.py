# Generated by Django 4.2.3 on 2025-02-02 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='isBan',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='reasonBan',
            field=models.CharField(default='', max_length=255),
        ),
    ]
