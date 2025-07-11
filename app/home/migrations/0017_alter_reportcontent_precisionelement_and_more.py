# Generated by Django 5.1.6 on 2025-06-11 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_usermoderationlog_model_usermoderationlog_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportcontent',
            name='precisionElement',
            field=models.CharField(choices=[('unknown', 'unknown'), ('image', 'image'), ('text', 'text'), ('music', 'music'), ('copyright', 'copyright')], max_length=25, verbose_name="precision sur l'élément"),
        ),
        migrations.AlterField(
            model_name='reportcontent',
            name='resultModerator',
            field=models.CharField(choices=[('INVALID', 'INVALID'), ('VALID', 'VALID'), ('SPAM', 'SPAM'), ('DUPLICATE', 'DUPLICATE'), ('OTHER', 'OTHER')], max_length=25, verbose_name='Resultat moderateur'),
        ),
    ]
