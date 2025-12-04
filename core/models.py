from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Announcement(models.Model):
    TARGET_CHOICES = (
        ('ALL', 'All Students'),
        ('BATCH', 'Specific Batch'),
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_type = models.CharField(max_length=10, choices=TARGET_CHOICES, default='ALL')
    # We will link to Batch in a ManyToMany or ForeignKey if needed, but for now let's keep it simple.
    # If target_type is BATCH, we might want to specify which batches.
    # Let's add a ManyToMany field to Batch, but Batch is in another app.
    # To avoid circular imports, we can use string reference 'batches.Batch'.
    target_batches = models.ManyToManyField('batches.Batch', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
