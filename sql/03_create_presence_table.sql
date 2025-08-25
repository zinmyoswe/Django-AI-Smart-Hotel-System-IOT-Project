CREATE TABLE IF NOT EXISTS presence_readings (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    timestamp BIGINT,
    datetime VARCHAR(50),
    presence_state VARCHAR(50),
    sensitivity INT,
    online_status VARCHAR(50)
);
