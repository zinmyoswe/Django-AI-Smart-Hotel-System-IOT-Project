from django.contrib import admin

# Register your models here.
from .models import Hotel, Floor, Room, Device, IAQReading, PresenceReading, RawData

admin.site.register(Hotel)
admin.site.register(Floor)
admin.site.register(Room)
admin.site.register(Device)
admin.site.register(IAQReading)
admin.site.register(PresenceReading)
admin.site.register(RawData)