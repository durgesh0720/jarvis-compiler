import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.core.cache import cache

class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"video_{self.room_id}"

        room_members = cache.get(self.room_id, [])
        print(f"User {self.channel_name} attempting to join room {self.room_id}")
        
        if room_members is None:
            print(f"Room {self.room_id} does not exist. Closing WebSocket.")
            await self.close()
            return

        print(f"User {self.channel_name} joined room {self.room_id}")

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
        sender_channel = self.channel_name  # Get sender

        if data.get("type") in ["offer", "answer", "candidate"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_sdp",
                    "message": data,
                    "sender": sender_channel  # Include sender
                }
            )

    async def send_sdp(self, event):
        # Prevent sending SDP back to the sender
        if self.channel_name != event["sender"]:
            await self.send(text_data=json.dumps(event["message"]))
