import json
from datetime import datetime, timezone

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Endpoint

import requests

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        print(f"Connected to {self.room_name} room.")
        print(f"Connected channel name: {self.channel_name}")

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        print(f"Disconnected from {self.room_name} room.")
        print(f"Disconnected channel name: {self.channel_name}")

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


class RoomConsumer(WebsocketConsumer):
    def connect(self):
        self.endpoint_code = self.scope["url_route"]["kwargs"]["endpoint_code"]
        # Get room name and user from endpoint code
        endpoint = Endpoint.objects.get(code=self.endpoint_code)
        # If the endpoint is not found, close the connection
        if endpoint is None:
            self.close()

        self.permissions = endpoint.permissions
        self.endpoint_identity = endpoint.identity
        self.room_name = endpoint.room.name
        # Get the room webhook address
        self.room_webhook = endpoint.room.webhook
        # Get the user name
        self.username = endpoint.room.owner.username
        # Get the room group name
        self.room_group_name = f"{self.username}_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        print(
            f"Connected endpoint_code {self.endpoint_code} to {self.room_name} room of user {self.username}."
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        print(f"Disconnected from {self.room_name} room.")
        print(f"Disconnected channel name: {self.channel_name}")
        self.close()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Add timestamp to the message using UTC timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        if "write" in self.permissions:
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "room.message",
                    "message": message,
                    "identity": self.endpoint_identity,
                    "timestamp": timestamp,
                },
            )
            # Send the message as json to webhook adress
            if self.room_webhook:
                # Send as a post request to the webhook
                data_json = json.dumps(
                    {
                        "message": message,
                        "identity": self.endpoint_identity,
                        "endpoint_code": self.endpoint_code,
                        "room_name": self.room_name,
                        "timestamp": timestamp,
                    }
                )
                # Send the data to the webhook
                _ = requests.post(self.room_webhook, data=data_json)
            else:
                # No webhook provided
                pass


        

    # Receive message from room group
    def room_message(self, event):
        if "read" in self.permissions:
            # Extract the message from the event
            message = event["message"]
            identity = event["identity"]
            timestamp = event["timestamp"]
            # Send message to WebSocket
            self.send(text_data=json.dumps({"message": message, "identity": identity, "timestamp": timestamp}))
