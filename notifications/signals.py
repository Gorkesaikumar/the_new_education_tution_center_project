from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.conf import settings

from materials.models import StudyMaterial
from core.models import Announcement
from assignments.models import Assignment
from exams.models import Exam
from notifications.models import FCMToken
from notifications.services import (
    send_push_notification, 
    notify_batch_students, 
    notify_all_students
)

import logging

logger = logging.getLogger(__name__)

# --- SYSTEM TRIGGERS ---

@receiver(post_save, sender=StudyMaterial)
def notify_new_material(sender, instance, created, **kwargs):
    if created:
        batch_id = instance.batch.id
        notify_batch_students(
            [batch_id],
            title="New Study Material",
            body=f"{instance.title} has been uploaded for {instance.subject.name if instance.subject else ''}.",
            click_action="/materials/"
        )

@receiver(post_save, sender=Announcement)
def notify_new_announcement(sender, instance, created, **kwargs):
    """
    Handle global announcements immediately. 
    Batch specific ones are handled by m2m_changed below.
    """
    if created and instance.target_type == 'ALL':
        notify_all_students(
            title=f"Announcement: {instance.title}",
            body=instance.content[:100],
            click_action="/announcements/"
        )

@receiver(m2m_changed, sender=Announcement.target_batches.through)
def notify_batch_announcement(sender, instance, action, **kwargs):
    if action == "post_add" and instance.target_type == 'BATCH':
        batch_ids = list(instance.target_batches.values_list('id', flat=True))
        notify_batch_students(
            batch_ids,
            title=f"Batch Update: {instance.title}",
            body=instance.content[:100],
            click_action="/announcements/"
        )

@receiver(post_save, sender=Assignment)
def notify_new_assignment(sender, instance, created, **kwargs):
    if created:
        notify_batch_students(
            [instance.batch.id],
            title="New Assignment",
            body=f"{instance.title} - Due: {instance.due_date.strftime('%b %d')}",
            click_action=f"/assignments/{instance.pk}/"
        )

@receiver(post_save, sender=Exam)
def notify_exam_schedule(sender, instance, created, **kwargs):
    title = "New Exam Scheduled" if created else "Exam Schedule Updated"
    notify_batch_students(
        [instance.batch.id],
        title=title,
        body=f"{instance.title} is set for {instance.date.strftime('%b %d, %Y')}.",
        click_action="/exams/"
    )

from attendance.models import AttendanceRecord

@receiver(post_save, sender=AttendanceRecord)
def notify_attendance_alert(sender, instance, created, **kwargs):
    """
    Notify student ONLY if they are marked ABSENT.
    """
    if instance.status == 'ABSENT':
        send_push_notification(
            [instance.student.id],
            title="Attendance Alert",
            body=f"You were marked ABSENT for {instance.batch.name} on {instance.date}.",
            click_action="/attendance/my-attendance/"
        )

# --- SECURITY TRIGGERS ---

@receiver(user_logged_out)
def deactivate_fcm_tokens_on_logout(sender, request, user, **kwargs):
    """
    Deactivate all FCM tokens for the user when they log out 
    to prevent unauthorized notifications on shared devices.
    """
    if user:
        FCMToken.objects.filter(user=user).update(is_active=False)
        logger.info(f"Deactivated FCM tokens for user: {user.username} on logout.")
