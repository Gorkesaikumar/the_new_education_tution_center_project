from django.conf import settings

def firebase_settings(request):
    """
    Expose Firebase configuration settings to all templates.
    """
    return {
        'FIREBASE_API_KEY': getattr(settings, 'FIREBASE_API_KEY', ''),
        'FIREBASE_AUTH_DOMAIN': getattr(settings, 'FIREBASE_AUTH_DOMAIN', ''),
        'FIREBASE_PROJECT_ID': getattr(settings, 'FIREBASE_PROJECT_ID', ''),
        'FIREBASE_STORAGE_BUCKET': getattr(settings, 'FIREBASE_STORAGE_BUCKET', ''),
        'FIREBASE_MESSAGING_SENDER_ID': getattr(settings, 'FIREBASE_MESSAGING_SENDER_ID', ''),
        'FIREBASE_APP_ID': getattr(settings, 'FIREBASE_APP_ID', ''),
        'FIREBASE_VAPID_KEY': getattr(settings, 'FIREBASE_VAPID_KEY', ''),
        'FIREBASE_MEASUREMENT_ID': getattr(settings, 'FIREBASE_MEASUREMENT_ID', ''),
    }
