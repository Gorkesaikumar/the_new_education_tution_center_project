import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from .models import FCMToken
import logging

logger = logging.getLogger(__name__)

def _initialize_firebase():
    """
    Initialize Firebase Admin SDK if not already initialized.
    """
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            return False
    return True

def send_push_notification(user_ids, title, body, data=None, click_action=None):
    """
    Send push notifications to a list of users.
    Handles multiple devices per user and removes invalid tokens.
    """
    if not _initialize_firebase():
        return False

    # Get all active tokens for these users
    tokens_queryset = FCMToken.objects.filter(
        user_id__in=user_ids,
        is_active=True
    )
    
    if not tokens_queryset.exists():
        logger.warning(f"No active tokens found for users: {user_ids}")
        return False

    tokens_list = list(tokens_queryset.values_list('token', flat=True))
    
    # Firebase Cloud Messaging supports batching up to 500 tokens per call
    batch_size = 500
    for i in range(0, len(tokens_list), batch_size):
        batch = tokens_list[i:i + batch_size]
        
        # Prepare message
        # We include notification info in BOTH 'notification' and 'data' blocks
        # to ensure maximum compatibility with different mobile browsers and background states.
        message_data = data or {}
        message_data.update({
            'title': title,
            'body': body,
            'url': click_action or "/"
        })

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=message_data,
            tokens=batch
        )

        try:
            response = messaging.send_each_for_multicast(message)
            _handle_batch_response(response, batch)
            logger.info(f"Successfully sent {response.success_count} notifications.")
        except Exception as e:
            logger.error(f"Error sending multicast message: {e}")

    return True

def _handle_batch_response(response, tokens):
    """
    Cleanup invalid/expired tokens based on Firebase response.
    """
    if response.failure_count > 0:
        responses = response.responses
        invalid_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # Common errors: Unregistered, InvalidArgument, etc.
                # If unregistered, the token is no longer valid.
                err_code = resp.exception.code if hasattr(resp.exception, 'code') else str(resp.exception)
                if err_code in ['messaging/registration-token-not-registered', 'messaging/invalid-registration-token']:
                    invalid_tokens.append(tokens[idx])
        
        if invalid_tokens:
            logger.info(f"Deactivating {len(invalid_tokens)} invalid tokens.")
            FCMToken.objects.filter(token__in=invalid_tokens).update(is_active=False)

def notify_batch_students(batch_ids, title, body, data=None, click_action=None):
    """
    Helper to notify all students in specific batches.
    """
    from core.models import User
    users = User.objects.filter(student_profile__batch_id__in=batch_ids, is_student=True)
    user_ids = list(users.values_list('id', flat=True))
    return send_push_notification(user_ids, title, body, data, click_action)

def notify_all_students(title, body, data=None, click_action=None):
    """
    Helper to notify all registered students.
    """
    from core.models import User
    users = User.objects.filter(is_student=True)
    user_ids = list(users.values_list('id', flat=True))
    return send_push_notification(user_ids, title, body, data, click_action)
