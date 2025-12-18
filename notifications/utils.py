import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Requires FIREBASE_SERVICE_ACCOUNT_KEY (path to JSON) in settings or environment.
    """
    if not firebase_admin._apps:
        try:
            # Check for service account key in environment variable or settings
            service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_KEY', None)
            if service_account_path:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                # Default behavior if no specific key is provided (e.g. on Google Cloud with Application Default Credentials)
                firebase_admin.initialize_app()
            logger.info("Firebase Admin SDK initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

def send_push_notification(user, title, body, data=None):
    """
    Send push notification to a specific user.
    """
    initialize_firebase()
    
    tokens = user.fcm_tokens.all().values_list('token', flat=True)
    if not tokens:
        logger.info(f"No FCM tokens found for user {user.username}")
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        tokens=list(tokens),
    )

    try:
        response = messaging.send_multicast(message)
        logger.info(f"Successfully sent {response.success_count} notifications for user {user.username}")
        
        # Cleanup invalid tokens
        if response.failure_count > 0:
            for index, result in enumerate(response.responses):
                if not result.success:
                    token = tokens[index]
                    # If token is invalid or not registered, delete it
                    if result.exception.code in ['invalid-registration-token', 'registration-token-not-registered']:
                        user.fcm_tokens.filter(token=token).delete()
                        logger.info(f"Deleted invalid token for user {user.username}")
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")

def send_bulk_push_notification(users, title, body, data=None):
    """
    Send push notifications to a list of users.
    Efficiently batches requests.
    """
    from .models import FCMToken
    
    tokens = list(FCMToken.objects.filter(user__in=users).values_list('token', flat=True))
    if not tokens:
        return

    initialize_firebase()
    
    # Firebase MulticastMessage supports up to 500 tokens at once
    for i in range(0, len(tokens), 500):
        batch = tokens[i:i + 500]
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=batch,
        )
        try:
            messaging.send_multicast(message)
        except Exception as e:
            logger.error(f"Error sending bulk push notification batch: {e}")
