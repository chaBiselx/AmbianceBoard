from django.db import migrations, models
from django.db.models import F


def copy_messages_to_english(apps, schema_editor):
    notification = apps.get_model('main', 'GeneralNotification')
    notification.objects.using(schema_editor.connection.alias).update(message_en=F('message'))


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_alter_useractivity_activity_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalnotification',
            name='message_en',
            field=models.TextField(
                blank=True,
                help_text="Message de la notification en anglais, en HTML",
                verbose_name="Message anglais (HTML)",
            ),
        ),
        migrations.RunPython(copy_messages_to_english, migrations.RunPython.noop),
    ]
