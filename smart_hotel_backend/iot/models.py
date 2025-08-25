from django.db import models

# -----------------------------
# Hotel / Floor / Room / Device
# -----------------------------
class Hotel(models.Model):
    name = models.CharField(max_length=100)

class Floor(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class Device(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50)
    device_type = models.CharField(max_length=50)

# ----------------------------
# Phase 1 / existing tables
# ----------------------------

# class RawData(models.Model):
#     timestamp = models.DateTimeField(db_column='datetime')  # use datetime column
#     device = models.ForeignKey(Device, on_delete=models.CASCADE, db_column='device_id')
#     datapoint = models.CharField(max_length=50)
#     value = models.FloatField()

class RawData(models.Model):
    timestamp = models.BigIntegerField()
    datetime = models.DateTimeField()
    device_id = models.CharField(max_length=100)
    datapoint = models.CharField(max_length=100)
    value = models.FloatField()

    class Meta:
        managed = False  # Django will not create or modify this table
        db_table = 'raw_data'

class IAQReading(models.Model):
    device_id = models.CharField(max_length=50)  # keep device_id as CharField
    temperature = models.FloatField()
    humidity = models.FloatField()
    co2 = models.FloatField()
    timestamp = models.DateTimeField(db_column='datetime')

    class Meta:
        db_table = "iaq_readings"
        managed = False

class PresenceReading(models.Model):
    device_id = models.CharField(max_length=50)  # keep device_id as CharField
    presence_state = models.CharField(max_length=20)
    sensitivity = models.IntegerField()
    online_status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(db_column='datetime')

    class Meta:
        db_table = "presence_readings"
        managed = False