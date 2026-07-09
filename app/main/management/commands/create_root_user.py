from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import Group

from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserPreference import UserPreference
from main.domain.common.utils.settings import Settings


ROOT_USERNAME = "root"
ROOT_EMAIL = "root@localhost"
ROOT_PASSWORD = "root"


class Command(BaseCommand):
    help = (
        "Cree (ou met a jour) un utilisateur root/root et lui attribue tous les roles. "
        "Commande reservee au mode DEBUG."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "La commande create_root_user est reservee a l'environnement DEBUG=1."
            )

        configured_groups = Settings.get("GROUPS", {})
        role_names = list(configured_groups.keys()) if isinstance(configured_groups, dict) else []

        user, created = User.objects.get_or_create(
            username=ROOT_USERNAME,
            defaults={
                "email": ROOT_EMAIL,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "isConfirmed": True,
            },
        )

        user.email = ROOT_EMAIL
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.isConfirmed = True
        user.set_password(ROOT_PASSWORD)
        user.save()

        UserPreference.objects.get_or_create(user=user)

        groups = []
        for role_name in role_names:
            group, _ = Group.objects.get_or_create(name=role_name)
            groups.append(group)

        user.groups.set(groups)

        action = "cree" if created else "mis a jour"
        self.stdout.write(
            self.style.SUCCESS(
                f"Utilisateur {ROOT_USERNAME} {action} avec succes. "
                f"Roles attribues: {', '.join(role_names) if role_names else 'aucun'}"
            )
        )