from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import FCMToken
import json

@login_required
@csrf_exempt # Token storage can be CSRF exempt if authenticated, or you can pass CSRF token in JS
def save_fcm_token(request):
    """
    Save or update an FCM token for the current user.
    Expects JSON: {"token": "...", "device_id": "..."}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            device_id = data.get('device_id')

            if not token:
                return JsonResponse({'status': 'error', 'message': 'Token missing'}, status=400)

            # Update or create token for this user
            # We use update_or_create to ensure we don't duplicate tokens for the same device if possible
            # or just get_or_create to avoid duplicates site-wide if the token is unique
            fcm_token, created = FCMToken.objects.get_or_create(
                token=token,
                defaults={'user': request.user, 'device_id': device_id}
            )
            
            if not created:
                fcm_token.user = request.user
                fcm_token.device_id = device_id
                fcm_token.save()

            return JsonResponse({'status': 'success', 'message': 'Token saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
