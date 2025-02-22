import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.core.cache import cache
# Create your views here.
@csrf_exempt
def create_room(request):
    if request.method == "POST":
        room_id = get_random_string(8)
        cache.set(room_id, [], timeout=3600)  # Store room ID in cache for 1 hour
        return JsonResponse({"room_id": room_id})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def join_room(request):
    if request.method == "POST":
        data = json.loads(request.body)
        room_id = data.get("room_id")
        if cache.get(room_id) is not None:
            return JsonResponse({"message": "Joined room"})
        return JsonResponse({"error": "Room not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)