from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Delete all users, then create a user named 'default' with empty api_key."

    def handle(self, *args, **options):
        User = get_user_model()

        with transaction.atomic():
            # Delete ALL users first (cascades will remove related rooms/endpoints)
            deleted_count, _ = User.objects.all().delete()

            # Create fresh default user
            default_user = User.objects.create(
                username="default",
                api_key="",
            )

            # Ensure it's a regular user with unusable password
            default_user.is_superuser = False
            default_user.is_staff = False
            default_user.set_unusable_password()
            default_user.save()

        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} user(s)."))
        self.stdout.write(self.style.SUCCESS("Created user 'default' with empty api_key."))
