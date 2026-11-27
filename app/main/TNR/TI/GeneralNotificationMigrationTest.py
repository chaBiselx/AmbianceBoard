from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase, tag
from django.utils import timezone


@tag('integration')
class GeneralNotificationMigrationTest(TransactionTestCase):
    migrate_from = [('main', '0040_alter_useractivity_activity_type')]
    migrate_to = [('main', '0041_generalnotification_message_en')]

    def test_existing_messages_are_copied_to_english(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        self.addCleanup(self.restore_migrations)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        notification = old_apps.get_model('main', 'GeneralNotification')
        now = timezone.now()
        messages = ['<p>Bonjour !</p>', '<strong>Deuxième message</strong>']
        for message in messages:
            notification.objects.create(
                message=message,
                start_date=now,
                end_date=now + timezone.timedelta(days=1),
            )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        new_apps = executor.loader.project_state(self.migrate_to).apps
        migrated = new_apps.get_model('main', 'GeneralNotification')

        self.assertCountEqual(
            migrated.objects.values_list('message', 'message_en'),
            [(message, message) for message in messages],
        )

    def restore_migrations(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
