from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from transactions.services import generate_demo_data

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds realistic transaction data into Django ORM database for N months'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=False,
            default=None,
            help='User email to attach transactions to (defaults to demo user if not given)'
        )
        parser.add_argument(
            '--months',
            type=int,
            default=6,
            help='Number of months of history to generate (default: 6)'
        )

    def handle(self, *args, **options):
        email = options.get('email')
        months = options.get('months', 6)

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with email '{email}' does not exist."))
                return
        else:
            user = User.objects.first()
            if not user:
                user = User.objects.create_user(
                    username="demouser",
                    email="demo@finagent.ai",
                    password="Password@123"
                )
                self.stdout.write(self.style.SUCCESS("Created default user 'demouser' (Password@123)."))

        count = generate_demo_data(user.id if user else None, months=months)

        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully generated and saved {count} transactions into Django ORM for user '{user.username if user else 'demo'}'. Total history: {months} months."
                )
            )
        else:
            self.stdout.write(self.style.WARNING("No transactions generated."))
