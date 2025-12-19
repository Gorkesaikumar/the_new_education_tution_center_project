from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User
from fees.models import FeePayment
from notifications.services import send_push_notification
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send push notifications to students with overdue fees'

    def handle(self, *args, **options):
        today = timezone.now().date()
        students = User.objects.filter(is_student=True, student_profile__isnull=False)
        sent_count = 0

        for user in students:
            profile = user.student_profile
            join_date = profile.date_of_join
            days_since_join = (today - join_date).days
            
            fee_due = False
            if days_since_join > 30:
                last_payment = FeePayment.objects.filter(student=user).order_by('-date').first()
                if not last_payment:
                    fee_due = True
                else:
                    days_since_payment = (today - last_payment.date).days
                    if days_since_payment > 30:
                        fee_due = True

            if fee_due:
                success = send_push_notification(
                    [user.id],
                    title="Fee Payment Reminder",
                    body="Your monthly fee is due. Please pay as soon as possible to avoid interruptions.",
                    click_action="/fees/history/"
                )
                if success:
                    sent_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully sent {sent_count} fee reminders.'))
