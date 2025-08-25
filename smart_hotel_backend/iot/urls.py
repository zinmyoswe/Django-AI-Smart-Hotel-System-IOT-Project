from django.urls import path
from . import views
from .views import RoomLatestData

urlpatterns = [
    # Hotel / Floor / Room
    path('hotels/', views.HotelList.as_view(), name='hotel-list'),
    path('hotels/<int:hotel_id>/floors/', views.FloorList.as_view(), name='floor-list'),
    path('floors/<int:floor_id>/rooms/', views.RoomList.as_view(), name='room-list'),

    # Latest IoT Data
    # path('rooms/<int:room_id>/data/', views.RoomLatestData.as_view(), name='room-latest-data'),
    # path('rooms/<int:room_id>/data/', views.RoomLatestData, name='room-latest-data'),
    # path('rooms/<int:room_id>/data/', views.RoomLatestData.as_view(), name='room-latest-data'),
    path('rooms/<int:room_id>/data/', RoomLatestData.as_view(), name='room-latest-data'),
    
    # path('rooms/<int:room_id>/data/iaq/', views.IAQLatestData.as_view(), name='iaq-latest-data'),
    path('rooms/<int:room_number>/data/iaq/', views.IAQLatestData.as_view(), name='iaq-latest-data'),
    # path('rooms/<int:room_id>/data/life_being/', views.LifeBeingLatestData.as_view(), name='presence-latest-data'),
    path('rooms/<int:room_number>/data/life_being/', views.LifeBeingLatestData.as_view(), name='presence-latest-data'),

    # Energy Summary
    # path('hotels/<int:hotel_id>/energy_summary/', views.EnergySummary.as_view(), name='energy-summary'),
    # path('hotels/<int:hotel_id>/energy_summary/', views.energy_summary, name='energy-summary'),
    path('hotels/<int:hotel_id>/energy_summary/', views.energy_summary, name='energy-summary'),
]
