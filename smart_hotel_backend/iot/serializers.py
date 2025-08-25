from rest_framework import serializers
from .models import Hotel, Floor, Room, RawData, IAQReading, PresenceReading

# Hotel / Floor / Room
class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name']

class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['id', 'hotel', 'name']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'floor', 'name']

# IoT Readings
class RawDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawData
        fields = ['timestamp', 'device_id', 'datapoint', 'value']




class IAQReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = IAQReading
        fields = ['device_id', 'temperature', 'humidity', 'co2', 'timestamp']

class PresenceReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresenceReading
        fields = ['device_id', 'presence_state', 'sensitivity', 'online_status', 'timestamp']
