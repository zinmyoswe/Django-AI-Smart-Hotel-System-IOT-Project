-- TimescaleDB raw_data schema (matches test spec)
CREATE TABLE IF NOT EXISTS raw_data (
    timestamp INTEGER,
    datetime TIMESTAMPTZ,
    device_id TEXT,
    datapoint TEXT,
    value TEXT
);