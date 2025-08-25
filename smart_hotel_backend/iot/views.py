from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Hotel, Floor, Room, Device, RawData, IAQReading, PresenceReading
from .serializers import HotelSerializer, FloorSerializer, RoomSerializer, RawDataSerializer, IAQReadingSerializer, PresenceReadingSerializer
from .utils import energy_summary
from django.http import JsonResponse
from django.db import connection
import csv
import pandas as pd
import datetime

# ----------------------------
# Hotel / Floor / Room APIs
# ----------------------------

class HotelList(generics.ListAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class FloorList(generics.ListAPIView):
    serializer_class = FloorSerializer

    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return Floor.objects.filter(hotel_id=hotel_id)

class RoomList(generics.ListAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        floor_id = self.kwargs['floor_id']
        return Room.objects.filter(floor_id=floor_id)

# ----------------------------
# Latest Data APIs
# ----------------------------

# class RoomLatestData(APIView):
#     def get(self, request, room_id):
#         # Get all devices in the room
#         devices = Device.objects.filter(room_id=room_id)
#         device_ids = devices.values_list('device_id', flat=True)
        
#         data = RawData.objects.filter(device_id__in=device_ids).order_by('-timestamp')[:1]
#         serializer = RawDataSerializer(data, many=True)
#         return Response(serializer.data)


class RoomLatestData(APIView):
    def get(self, request, room_id):
        # Get device_id for the room
        device_id = f"iaq_sensor_Room{room_id}"

        query = """
            SELECT datetime, datapoint, value
            FROM raw_data
            WHERE device_id = %s
            ORDER BY datetime DESC
            LIMIT 10
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [device_id])
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "datetime": row[0],
                "datapoint": row[1],
                "value": row[2]
            })

        return JsonResponse(data, safe=False)

# class IAQLatestData(APIView):
#     def get(self, request, room_id):
#         # Filter IAQ devices in this room
#         devices = Device.objects.filter(room_id=room_id, device_type='iaq')
#         device_ids = devices.values_list('device_id', flat=True)
        
#         data = IAQReading.objects.filter(device_id__in=device_ids).order_by('-timestamp')[:1]
#         serializer = IAQReadingSerializer(data, many=True)
#         return Response(serializer.data)


# Latest IAQ Data
class IAQLatestData(APIView):
    def get(self, request, room_number):
        # room_number ကို Room.name နဲ့ match လုပ်ပြီး id ရှာ
        try:
            room = Room.objects.get(name=f"Room {room_number}")
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        # Devices filter
        devices = Device.objects.filter(room=room, device_type='iaq')
        device_ids = devices.values_list('device_id', flat=True)

        # IAQReading filter
        data = IAQReading.objects.filter(device_id__in=device_ids).order_by('-timestamp')[:30]
        serializer = IAQReadingSerializer(data, many=True)
        return Response(serializer.data)

# class LifeBeingLatestData(APIView):
#     def get(self, request, room_id):
#         # Filter presence devices in this room
#         devices = Device.objects.filter(room_id=room_id, device_type='presence')
#         device_ids = devices.values_list('device_id', flat=True)
        
#         data = PresenceReading.objects.filter(device_id__in=device_ids).order_by('-timestamp')[:30]
#         serializer = PresenceReadingSerializer(data, many=True)
#         return Response(serializer.data)

class LifeBeingLatestData(APIView):
    def get(self, request, room_number):
        try:
            room = Room.objects.get(name=f"Room {room_number}")
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        # Room တွင်ရှိတဲ့ presence devices filter
        devices = Device.objects.filter(room=room, device_type='presence')
        device_ids = devices.values_list('device_id', flat=True)

        # Latest 10 readings
        data = PresenceReading.objects.filter(device_id__in=device_ids).order_by('-timestamp')[:30]
        serializer = PresenceReadingSerializer(data, many=True)
        return Response(serializer.data)

# ----------------------------
# Energy Summary API
# ----------------------------

# class EnergySummary(APIView):
#     def get(self, request, hotel_id):
#         resolution = request.GET.get('resolution', '1hour')
#         start_time = request.GET.get('start_time', None)
#         end_time = request.GET.get('end_time', None)
#         subsystems = request.GET.getlist('subsystem') or None

#         df = energy_summary(hotel_id, resolution, start_time, end_time, subsystems)

#         # Return CSV
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="energy_summary.csv"'
#         df.to_csv(path_or_buf=response, index=False)
#         return response




def energy_summary(request, hotel_id=1):
    resolution = request.GET.get("resolution", "1hour")

    # For simplicity, use all power meters for hotel 1
    meters = ['power_meter_1','power_meter_2','power_meter_3',
              'power_meter_4','power_meter_5','power_meter_6']

    query = """
    SELECT datetime, device_id, value
    FROM raw_data
    WHERE device_id IN %s
    ORDER BY datetime ASC
    """

    # Load data from DB
    df = pd.read_sql_query(query, connection, params=[tuple(meters)])

    # ✅ Convert value column to float
    df['value'] = df['value'].astype(float)
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Group by resolution
    if resolution == "1hour":
        df = df.groupby([pd.Grouper(key='datetime', freq='H'), 'device_id']).mean().reset_index()

    # Map device to subsystem
    device_to_subsystem = {
        'power_meter_1': 'ac',
        'power_meter_2': 'ac',
        'power_meter_3': 'ac',
        'power_meter_4': 'lighting',
        'power_meter_5': 'lighting',
        'power_meter_6': 'plug_load'
    }
    df['subsystem'] = df['device_id'].map(device_to_subsystem)
    df['energy_kwh'] = df['value'] * 1  # runhour = 1 per resolution

    # Aggregate per subsystem
    df_summary = df.groupby(['datetime','subsystem'])['energy_kwh'].sum().reset_index()

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="energy_summary.csv"'
    df_summary.to_csv(response, index=False)
    return response

