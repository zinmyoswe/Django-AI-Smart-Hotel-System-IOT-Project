# Smart Hotel — Phase 1 (On-Premise IoT Infrastructure)

This package contains Phase 1 deliverables: sensor agents (IAQ & Presence), RabbitMQ pub/sub, datalogger, TimescaleDB schema, and an optional Supabase "latest" store.

## Architecture (Phase 1)
See `architecture/phase1_architecture.png` or the ASCII below.

```
CSV (Room101/102/103)
   ├── IAQ Agent (per room) ----┐
   └── Presence Agent (per room) ├──> RabbitMQ Queue: `iot_data` ──> Datalogger
                                 │                                    ├── TimescaleDB (historical: raw_data)
                                 └────────────────────────────────────└── Supabase (latest per device, optional)
```

## Prerequisites
- Docker & Docker Compose
- Python 3.10+ (if running agents locally outside containers)

## Quick Start
1. Start infrastructure:
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```

2. Create the TimescaleDB table:
   ```bash
   docker exec -it timescaledb psql -U admin -d iotdb -f /docker-entrypoint-initdb.d/01_init_raw_data.sql
   ```

3. Put your CSV files into `data/` folder (example names):
   - `sample_iaq_data_Room101.csv`, `sample_iaq_data_Room102.csv`, `sample_iaq_data_Room103.csv`
   - `sample_presence_sensor_data_Room101.csv`, `sample_presence_sensor_data_Room102.csv`, `sample_presence_sensor_data_Room103.csv`

   Each IAQ CSV row example:
   ```csv
   timestamp,temperature,humidity,co2
   2025-08-22T10:00:00Z,24.5,45.2,450
   ```

   Each Presence CSV row example:
   ```csv
   timestamp,presence_state,sensitivity
   2025-08-22T10:00:00Z,occupied,high
   ```

4. (Locally) Install Python deps (optional if not using Docker for agents):
   ```bash
   pip install -r requirements.txt
   ```

5. Run agents (examples):
   ```bash
   python agents/iaq_agent.py Room101
   python agents/presence_agent.py Room101
   ```

6. Run datalogger:
   ```bash
   python datalogger/datalogger.py
   ```

## Environment Variables (for Datalogger)
- `DB_HOST` (default `localhost`)
- `DB_PORT` (default `5432`)
- `DB_NAME` (default `iotdb`)
- `DB_USER` (default `admin`)
- `DB_PASSWORD` (default `admin`)

Optional Supabase (latest store):
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_TABLE` (default `latest_sensor_data`)

If Supabase vars are missing, datalogger will skip Supabase updates.

## Notes
- Queue name: `iot_data`
- Publish interval: 5 seconds per row
- `raw_data` schema matches the test spec (TEXT for `value` to support strings).