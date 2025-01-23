from django.urls import path

from . import views



urlpatterns = [
    path("", views.index, name="index"),
    path("room/<str:endpoint_code>/", views.room, name="room"),
    path("create_room/<str:room_name>/", views.create_room, name="create_room"),
    path("list_rooms/", views.list_rooms, name="list_rooms"),
    path("delete_room/<str:room_name>/", views.delete_room, name="delete_room"),
    path("add_endpoint/<str:room_name>/<str:permissions>/", views.add_endpoint, name="add_endpoint"),
    path("delete_endpoint/<str:room_name>/<str:endpoint_code>/", views.delete_endpoint, name="delete_endpoint"),
    path("list_endpoints/<str:room_name>/", views.list_endpoints, name="list_endpoints"),

]