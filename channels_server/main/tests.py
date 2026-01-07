import json
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from channels_server.asgi import application
from .models import Endpoint, Room


User = get_user_model()


class ViewTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="alice", password="pass", api_key="valid-key"
		)
		self.client.defaults["HTTP_API_KEY"] = "valid-key"
		self.room = Room.objects.create(name="alpha", owner=self.user, webhook="")

	def test_create_room_requires_post(self):
		response = self.client.get(reverse("create_room"))
		self.assertEqual(response.status_code, 404)

	def test_create_room_rejects_missing_api_key(self):
		self.client.defaults.pop("HTTP_API_KEY", None)
		response = self.client.post(reverse("create_room"), data={}, content_type="application/json")
		self.assertEqual(response.status_code, 403)

	def test_create_room_creates_and_updates_webhook(self):
		payload = json.dumps({"room_name": "beta", "webhook": "https://example.com/hook"})
		response = self.client.post(
			reverse("create_room"), data=payload, content_type="application/json"
		)
		self.assertEqual(response.status_code, 200)
		room = Room.objects.get(name="beta", owner=self.user)
		self.assertEqual(room.webhook, "https://example.com/hook")

		# Update existing webhook
		updated_payload = json.dumps({"room_name": "beta", "webhook": "https://example.com/new"})
		update_response = self.client.post(
			reverse("create_room"), data=updated_payload, content_type="application/json"
		)
		self.assertEqual(update_response.status_code, 200)
		room.refresh_from_db()
		self.assertEqual(room.webhook, "https://example.com/new")

	def test_list_rooms_returns_owned_rooms(self):
		response = self.client.get(reverse("list_rooms"))
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertIn("alpha", data)
		self.assertEqual(data["alpha"]["owner"], self.user.username)

	def test_add_endpoint_creates_endpoint_and_returns_code(self):
		payload = json.dumps({"identity": "bot", "room_name": "alpha", "permissions": "readwrite"})
		response = self.client.post(
			reverse("add_endpoint"), data=payload, content_type="application/json"
		)
		self.assertEqual(response.status_code, 200)
		data = response.json()
		endpoint = Endpoint.objects.get(code=data["code"])
		self.assertEqual(endpoint.room, self.room)
		self.assertEqual(len(endpoint.code), 100)
		self.assertEqual(endpoint.identity, "bot")

	def test_list_endpoints_and_delete_endpoint(self):
		endpoint = Endpoint.objects.create(
			code="code123", permissions="readwrite", room=self.room, identity="client"
		)

		list_response = self.client.get(reverse("list_endpoints", args=["alpha"]))
		self.assertEqual(list_response.status_code, 200)
		payload = list_response.json()["endpoints"][0]
		self.assertEqual(payload["code"], endpoint.code)

		delete_response = self.client.get(reverse("delete_endpoint", args=["alpha", "code123"]))
		self.assertEqual(delete_response.status_code, 200)
		self.assertFalse(Endpoint.objects.filter(code="code123").exists())

	def test_delete_room_removes_room(self):
		response = self.client.get(reverse("delete_room", args=["alpha"]))
		self.assertEqual(response.status_code, 200)
		self.assertFalse(Room.objects.filter(name="alpha", owner=self.user).exists())


@override_settings(
	CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class RoomConsumerTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="bob", password="pass", api_key="bob-key"
		)
		self.room = Room.objects.create(name="chat", owner=self.user, webhook="")
		self.sender = Endpoint.objects.create(
			code="sendercode",
			permissions="readwrite",
			room=self.room,
			identity="sender",
		)
		self.receiver = Endpoint.objects.create(
			code="receivercode",
			permissions="readwrite",
			room=self.room,
			identity="receiver",
		)
		self.writer_only = Endpoint.objects.create(
			code="writeronly",
			permissions="write",
			room=self.room,
			identity="writer",
		)

	def test_readwrite_endpoints_receive_broadcasts(self):
		async def run_test():
			communicator_sender = WebsocketCommunicator(
				application, f"/ws/endpoint/{self.sender.code}/"
			)
			communicator_receiver = WebsocketCommunicator(
				application, f"/ws/endpoint/{self.receiver.code}/"
			)

			connected_sender, _ = await communicator_sender.connect()
			connected_receiver, _ = await communicator_receiver.connect()
			self.assertTrue(connected_sender)
			self.assertTrue(connected_receiver)

			await communicator_sender.send_json_to({"message": "hello"})
			response = await communicator_receiver.receive_json_from()
			self.assertEqual(response["message"], "hello")
			self.assertEqual(response["identity"], "sender")
			self.assertIn("timestamp", response)

			await communicator_sender.disconnect()
			await communicator_receiver.disconnect()

		async_to_sync(run_test)()

	def test_write_only_endpoint_does_not_read(self):
		async def run_test():
			writer = WebsocketCommunicator(application, f"/ws/endpoint/{self.writer_only.code}/")
			reader = WebsocketCommunicator(application, f"/ws/endpoint/{self.receiver.code}/")

			connected_writer, _ = await writer.connect()
			connected_reader, _ = await reader.connect()
			self.assertTrue(connected_writer)
			self.assertTrue(connected_reader)

			await writer.send_json_to({"message": "ping"})
			payload = await reader.receive_json_from()
			self.assertEqual(payload["message"], "ping")
			self.assertEqual(payload["identity"], "writer")

			nothing = await writer.receive_nothing()
			self.assertTrue(nothing)

			await writer.disconnect()
			await reader.disconnect()

		async_to_sync(run_test)()
