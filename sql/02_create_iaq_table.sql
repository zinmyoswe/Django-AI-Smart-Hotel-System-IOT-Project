CREATE TABLE IF NOT EXISTS iaq_readings (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    timestamp BIGINT,
    datetime VARCHAR(50),
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    co2 DOUBLE PRECISION
);
