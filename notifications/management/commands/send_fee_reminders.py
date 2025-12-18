from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from students.models import StudentProfile
from notifications.utils import send_push_notification
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send fee reminder notifications to students who joined 30 days ago and have pending fees.'

    def handle(self, *args, **options):
        # Calculate the date 30 days ago
        target_date = timezone.now().date() - timedelta(days=30)
        
        # Find students who joined on or before this date and have pending fees
        # We also want to avoid spamming. In a real app, we might store 'last_reminder_sent'
        # For this requirement, we'll send it if they are exactly 30 days or more and status is Pending.
        # User requested: "joined ... 30 days have passed ... status is Pending"
        
        pending_students = StudentProfile.objects.filter(
            date_of_join__lte=target_date,
            fee_status='Pending'
        ).select_related('user')

        sent_count = 0
        for student in pending_students:
            try:
                send_push_notification(
                    student.user,
                    title="Fee Reminder - Shoeb Sir's Academy",
                    body=f"Hi {student.user.first_name or student.user.username}, a month has passed since you joined. Please clear your pending fees.",
                    data={"url": "/fees/"} # Adjust URL to your actual fee payment page
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send fee reminder to {student.user.username}: {e}")

        self.stdout.write(self.style.SUCCESS(f'Successfully sent {sent_count} fee reminders.'))
