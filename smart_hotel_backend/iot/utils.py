import pandas as pd
from .models import RawData, Room

# Device mapping to subsystems
SUBSYSTEM_MAP = {
    'ac': ['power_meter_1', 'power_meter_2', 'power_meter_3'],
    'lighting': ['power_meter_4', 'power_meter_5'],
    'plug_load': ['power_meter_6']
}

# Hours per resolution for energy calculation
HOURS_MAP = {'H': 1, 'D': 24, 'M': 720}  # Month ~ 30 days

def energy_summary(hotel_id, resolution='1hour', start_time=None, end_time=None, subsystems=None):
    """
    Returns aggregated energy consumption DataFrame for a hotel.
    """
    # Step 1: Get all room names for the hotel
    room_names = Room.objects.filter(floor__hotel_id=hotel_id).values_list('name', flat=True)
    room_filters = [f'Room{name}' for name in room_names]

    # Step 2: Filter RawData by power_kw, hotel rooms
    qs = RawData.objects.filter(datapoint='power_kw')

    if room_filters:
        from django.db.models import Q
        q_filter = Q(device_id__icontains=room_filters[0])
        for rf in room_filters[1:]:
            q_filter |= Q(device_id__icontains=rf)
        qs = qs.filter(q_filter)

    # Step 3: Filter by subsystems
    if subsystems:
        device_list = []
        for sub in subsystems:
            device_list.extend(SUBSYSTEM_MAP.get(sub, []))
        qs = qs.filter(device_id__in=device_list)

    # Step 4: Filter by start/end time
    if start_time:
        qs = qs.filter(timestamp__gte=start_time)
    if end_time:
        qs = qs.filter(timestamp__lte=end_time)

    # Step 5: Convert queryset to DataFrame
    df = pd.DataFrame(list(qs.values('timestamp', 'device_id', 'value')))
    if df.empty:
        return pd.DataFrame(columns=['timestamp', 'subsystem', 'energy_kwh'])

    # Step 6: Map device_id to subsystem
    device_to_subsystem = {v: k for k, lst in SUBSYSTEM_MAP.items() for v in lst}
    df['subsystem'] = df['device_id'].map(device_to_subsystem)

    # Step 7: Set timestamp as datetime index
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Step 8: Resample by resolution
    rule_map = {'1hour': 'H', '1day': 'D', '1month': 'M'}
    resample_rule = rule_map.get(resolution, 'H')

    summary = df.groupby('subsystem')['value'].resample(resample_rule).mean().reset_index()

    # Step 9: Calculate energy consumption (kWh)
    summary['energy_kwh'] = summary['value'] * HOURS_MAP[resample_rule]

    # Step 10: Return final DataFrame
    return summary[['timestamp', 'subsystem', 'energy_kwh']]
