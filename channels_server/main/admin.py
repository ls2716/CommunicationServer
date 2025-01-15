from django.contrib import admin
from .models import CustomUser, Room, Endpoint

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Room)
admin.site.register(Endpoint)