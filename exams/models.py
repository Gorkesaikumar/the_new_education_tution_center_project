from django.db import models
from django.conf import settings

class Exam(models.Model):
    title = models.CharField(max_length=200)
    batch = models.ForeignKey('batches.Batch', on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey('batches.Subject', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.batch.name}"

class Mark(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}: {self.marks_obtained}"
