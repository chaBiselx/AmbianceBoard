# Generated by Django 5.1.6 on 2025-06-25 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_sharedsoundboard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='music',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
