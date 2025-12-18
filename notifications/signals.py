from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.conf import settings
from materials.models import StudyMaterial
from core.models import Announcement
from assignments.models import Assignment
from exams.models import Exam
from .utils import send_bulk_push_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=StudyMaterial)
def notify_new_material(sender, instance, created, **kwargs):
    if created:
        students = instance.batch.students.all().values_list('user', flat=True)
        from core.models import User
        users = User.objects.filter(id__in=students)
        
        send_bulk_push_notification(
            users,
            title="New Study Material",
            body=f"New material: {instance.title} for {instance.subject.name if instance.subject else ''}",
            data={"url": "/materials/"}
        )

@receiver(post_save, sender=Announcement)
def notify_new_announcement(sender, instance, created, **kwargs):
    if created and instance.target_type == 'ALL':
        from core.models import User
        users = User.objects.filter(is_student=True)
        send_bulk_push_notification(
            users,
            title="Important Announcement",
            body=instance.title,
            data={"url": "/announcements/"}
        )
    # Batch specific announcements are handled by m2m_changed if target_batches is used
    # But for simplicity, we'll wait for m2m_changed signal if it's BATCH type

@receiver(m2m_changed, sender=Announcement.target_batches.through)
def notify_batch_announcement(sender, instance, action, **kwargs):
    if action == "post_add" and instance.target_type == 'BATCH':
        from core.models import User
        # Get users from all targeted batches
        batches = instance.target_batches.all()
        users = User.objects.filter(student_profile__batch__in=batches).distinct()
        
        send_bulk_push_notification(
            users,
            title="Batch Announcement",
            body=instance.title,
            data={"url": "/announcements/"}
        )

@receiver(post_save, sender=Assignment)
def notify_new_assignment(sender, instance, created, **kwargs):
    if created:
        students = instance.batch.students.all().values_list('user', flat=True)
        from core.models import User
        users = User.objects.filter(id__in=students)
        
        send_bulk_push_notification(
            users,
            title="New Assignment",
            body=f"Assignment: {instance.title}. Due on {instance.due_date.strftime('%M %d, %H:%I')}",
            data={"url": f"/assignments/{instance.pk}/"}
        )

@receiver(post_save, sender=Exam)
def notify_exam_update(sender, instance, created, **kwargs):
    title = "New Exam Scheduled" if created else "Exam Schedule Updated"
    
    students = instance.batch.students.all().values_list('user', flat=True)
    from core.models import User
    users = User.objects.filter(id__in=students)
    
    send_bulk_push_notification(
        users,
        title=title,
        body=f"Exam: {instance.title} on {instance.date.strftime('%M %d, %Y')}",
        data={"url": "/exams/"}
    )
