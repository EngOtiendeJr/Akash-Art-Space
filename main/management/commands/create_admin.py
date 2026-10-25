
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from main.constants import MAX_ADMIN_USERS


class Command(BaseCommand):
    help = "Create or update the production administrator"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not all([username, email, password]):
            raise CommandError(
                "ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD "
                "must be configured."
            )

        User = get_user_model()

        if User.USERNAME_FIELD != "username":
            raise CommandError(
                "This command expects Django's standard username field."
            )

        user = User.objects.filter(username=username).first()

        if user is None:
            staff_users = User.objects.filter(is_staff=True).count()
            if staff_users >= MAX_ADMIN_USERS:
                raise CommandError(
                    f"Cannot create another administrator: only {MAX_ADMIN_USERS} "
                    "Django Admin accounts are allowed."
                )
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        else:
            if not user.is_staff:
                staff_users = User.objects.filter(is_staff=True).count()
                if staff_users >= MAX_ADMIN_USERS:
                    raise CommandError(
                        f"Cannot promote this account: only {MAX_ADMIN_USERS} "
                        "Django Admin accounts are allowed."
                    )
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()

        self.stdout.write(
            self.style.SUCCESS("Production administrator configured.")
        )
