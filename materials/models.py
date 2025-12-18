from django.db import models
from django.conf import settings


class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    file = models.FileField(
        upload_to="study_materials/",
        null=True,
        blank=True,
    )

    batch = models.ForeignKey(
        "batches.Batch",
        on_delete=models.CASCADE,
        related_name="materials",
    )

    subject = models.ForeignKey(
        "batches.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title

    @property
    def file_url(self):
        """
        Safe access for templates.
        Prevents 500 errors if file is missing.
        """
        try:
            if self.file and self.file.name:
                return self.file.url
        except (ValueError, AttributeError):
            pass
        return ""

    @property
    def has_file(self):
        """Check if material has a valid file attached."""
        try:
            return bool(self.file and self.file.name)
        except (ValueError, AttributeError):
            return False
