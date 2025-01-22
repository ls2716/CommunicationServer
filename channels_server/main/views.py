from django.shortcuts import render, get_object_or_404
from .models import CustomUser, Room, Endpoint
from django.http import (
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponse,
    JsonResponse,
)
import random


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


def create_room(request, room_name):
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")

    # Check if the room already exists
    if Room.objects.filter(name=room_name).exists():
        return HttpResponseNotFound("Room already exists")
    # Create a new room
    Room.objects.create(name=room_name, owner=user)
    return HttpResponse("Room created successfully")


def delete_room(request, room_name):
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY")
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
    api_key = request.headers.get("API-KEY")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    # Get all rooms for the user
    rooms = Room.objects.filter(owner=user)
    return JsonResponse({"rooms": [room.name for room in rooms]})


def add_endpoint(request, room_name, permissions):
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY")
    user = get_user(api_key)
    if user is None:
        return HttpResponseForbidden("No/Invalid API KEY")
    # Get the room or return 404
    room = get_object_or_404(Room, name=room_name, owner=user)

    # Get idenity from the request query params
    identity = request.GET.get("identity", "Anonymous")

    # Check if the permissions are valid
    if permissions not in ["read", "write", "readwrite"]:
        return HttpResponseNotFound(
            "Invalid permissions: The permissions should be read, write or readwrite"
        )

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
        {"code": endpoint_code, "permissions": permissions, "room": room_name}
    )


def delete_endpoint(request, room_name, endpoint_code):
    # Get the API KEY from header
    api_key = request.headers.get("API-KEY")
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
    api_key = request.headers.get("API-KEY")
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
