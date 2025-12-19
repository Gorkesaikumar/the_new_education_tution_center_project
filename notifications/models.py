from django.db import models
from django.conf import settings

class FCMToken(models.Model):
    DEVICE_TYPES = (
        ('WEB', 'Web Browser'),
        ('MOBILE', 'Mobile App'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.TextField(unique=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES, default='WEB')
    browser = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FCM Token"
        verbose_name_plural = "FCM Tokens"
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.device_type} ({self.browser or 'Unknown'})"
