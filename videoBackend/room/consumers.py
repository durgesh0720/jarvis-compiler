import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.core.cache import cache
from asgiref.sync import sync_to_async

class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"video_{self.room_id}"
        
        if cache.get(self.room_id) is None:
            await self.close()
            return
        
        room_members = cache.get(self.room_id)
        room_members.append(self.channel_name)
        cache.set(self.room_id, room_members, timeout=3600)
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        room_members = cache.get(self.room_id, [])
        if self.channel_name in room_members:
            room_members.remove(self.channel_name)
            if not room_members:
                cache.delete(self.room_id)
            else:
                cache.set(self.room_id, room_members, timeout=3600)
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send.sdp",
                "message": data
            }
        )

    async def send_sdp(self, event):
        await self.send(text_data=json.dumps(event["message"]))
