from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.models import FCMToken
from datetime import timedelta

class Command(BaseCommand):
    help = 'Cleanup inactive or old FCM tokens'

    def handle(self, *args, **options):
        # 1. Cleanup tokens marked as inactive more than 30 days ago
        inactive_cutoff = timezone.now() - timedelta(days=30)
        deleted_inactive, _ = FCMToken.objects.filter(
            is_active=False, 
            updated_at__lt=inactive_cutoff
        ).delete()

        # 2. Cleanup tokens not used for more than 90 days (assumed abandoned)
        stale_cutoff = timezone.now() - timedelta(days=90)
        deleted_stale, _ = FCMToken.objects.filter(
            last_used_at__lt=stale_cutoff
        ).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Cleaned up {deleted_inactive} inactive tokens and {deleted_stale} stale tokens.'
        ))
