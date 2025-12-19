from django.core.management.base import BaseCommand
from core.models import User
from notifications.services import send_push_notification

class Command(BaseCommand):
    help = 'Send a test push notification to a specific user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the student to notify')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' does not exist."))
            return

        self.stdout.write(f"Sending test notification to {user.username}...")
        
        success = send_push_notification(
            user_ids=[user.id],
            title="Test! 🚀",
            body="If you see this, your notifications are working perfectly!",
            click_action="/"
        )

        if success:
            self.stdout.write(self.style.SUCCESS(f"Successfully sent test notification to {user.username}"))
        else:
            self.stdout.write(self.style.WARNING("Notification not sent. Make sure the user has enabled notifications and has an active token in the database."))
