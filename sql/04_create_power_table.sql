CREATE TABLE IF NOT EXISTS power_readings (
    id SERIAL PRIMARY KEY,
    device_id TEXT,
    timestamp BIGINT,
    datetime TIMESTAMPTZ,
    power_kw DOUBLE PRECISION
);
