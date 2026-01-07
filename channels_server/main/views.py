from django.shortcuts import render, get_object_or_404
from .models import CustomUser, Room, Endpoint
from django.http import (
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponse,
    JsonResponse,
)
import random
import json

# Import csrf_exempt
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return render(request, "main/index.html")


def room(request, endpoint_code):
    return render(request, "main/room.html", {"endpoint_code": endpoint_code})


def room_bad(request, endpoint_code):
    return render(request, "main/room_bad.html", {"endpoint_code": endpoint_code})


def get_user(api_key):
    try:
        return CustomUser.objects.get(api_key=api_key)
    except CustomUser.DoesNotExist:
        return None

@csrf_exempt
def create_room(request):
    if request.method != "POST":
        return HttpResponseNotFound("Invalid request method")
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY", "")
    print("API KEY '", api_key, "'", sep="")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    
    # Get data from json
    data = json.loads(request.body)

    room_name = data.get("room_name", None)
    if room_name is None:
        return HttpResponseBadRequest("Invalid room name")
    webhook = data.get("webhook", '')

    # Check if the room already exists
    if Room.objects.filter(name=room_name, owner=user).exists():
        # If so modify the webhook
        room = Room.objects.get(name=room_name, owner=user)
        room.webhook = webhook
        room.save()
        return HttpResponse("Room already exists. Webhook updated successfully.")
    # Create a new room
    Room.objects.create(name=room_name, owner=user, webhook=webhook)
    return HttpResponse("Room created successfully")


def delete_room(request, room_name):
    
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY", "")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")

    # Get the room or return 404
    room = get_object_or_404(Room, name=room_name, owner=user)
    # Delete the room
    room.delete()
    return HttpResponse("Room deleted successfully")


def list_rooms(request):
    # Get API KEY
    api_key = request.headers.get("API-KEY", "")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    # Get all rooms for the user
    rooms = Room.objects.filter(owner=user)
    room_dict = {}
    for room in rooms:
        room_dict[room.name] = {
            "webhook": room.webhook,
            "room_name": room.name,
            "owner": room.owner.username
        }
    return JsonResponse(room_dict)

@csrf_exempt
def add_endpoint(request):
    if request.method != "POST":
        return HttpResponseNotFound("Invalid request method")
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY", "")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    

    # Get data from json
    data = json.loads(request.body)

    # Get identity, room_name and permissions from the data
    identity = data.get("identity", "Anonymous")
    room_name = data.get("room_name", None)
    permissions = data.get("permissions", None)

    # Check if the room name is valid
    if room_name is None:
        return HttpResponseBadRequest("Invalid room name")
    if permissions is None:
        return HttpResponseBadRequest("Invalid permissions: The permissions should be read, write or readwrite")

    # Get the room or return 404
    room = get_object_or_404(Room, name=room_name, owner=user)

    # Generate random 100 character code
    endpoint_code = "".join(
        random.choices(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=100
        )
    )

    # Create a new endpoint
    Endpoint.objects.create(
        code=endpoint_code, permissions=permissions, room=room, identity=identity
    )

    return JsonResponse(
        {"code": endpoint_code, "permissions": permissions, "room_name": room_name, "identity": identity}
    )


def delete_endpoint(request, room_name, endpoint_code):
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY", "")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    # Get the room or return 404
    room = get_object_or_404(Room, name=room_name, owner=user)
    # Get the endpoint or return 404
    endpoint = get_object_or_404(Endpoint, code=endpoint_code, room=room)
    # Delete the endpoint
    endpoint.delete()
    return HttpResponse("Endpoint deleted successfully")


def list_endpoints(request, room_name):
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY", "")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    # Get the room or return 404
    room = get_object_or_404(Room, name=room_name, owner=user)
    # Get all endpoints for the room
    endpoints = Endpoint.objects.filter(room=room)
    return JsonResponse(
        {
            "endpoints": [
                {
                    "code": endpoint.code,
                    "permissions": endpoint.permissions,
                    "identity": endpoint.identity,
                }
                for endpoint in endpoints
            ]
        }
    )

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        # Get the data as json - the request is asgi request
        _ = json.loads(request.body)
        # print(_)
        return HttpResponse("Webhook received", status=200)
    else:
        return HttpResponseNotFound("Invalid request method")

        