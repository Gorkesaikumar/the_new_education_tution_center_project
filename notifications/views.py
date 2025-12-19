from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import FCMToken
import json

@login_required
@csrf_exempt
def save_fcm_token(request):
    """
    Save or update an FCM token for the current user.
    Expects JSON: {"token": "...", "device_id": "...", "device_type": "WEB", "browser": "..."}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            device_id = data.get('device_id')
            device_type = data.get('device_type', 'WEB')
            browser = data.get('browser')

            if not token:
                return JsonResponse({'status': 'error', 'message': 'Token missing'}, status=400)

            from django.utils import timezone
            
            # Using update_or_create on the token string as it is unique
            fcm_token, created = FCMToken.objects.update_or_create(
                token=token,
                defaults={
                    'user': request.user,
                    'device_id': device_id,
                    'device_type': device_type,
                    'browser': browser,
                    'is_active': True,
                    'last_used_at': timezone.now()
                }
            )

            return JsonResponse({
                'status': 'success', 
                'message': 'Token registered successfully',
                'created': created
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
