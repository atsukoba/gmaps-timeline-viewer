DROP TABLE IF EXISTS place;

CREATE TABLE place (
    name text,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    address text,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL
);

-- Distance Calculation Function
CREATE
OR REPLACE FUNCTION distance(
    lat1 double precision,
    lon1 double precision,
    lat2 double precision,
    lon2 double precision
) RETURNS double precision AS $BODY$ DECLARE R integer = 6371e3;
-- Meters
rad double precision = 0.01745329252;
φ1 double precision = lat1 * rad;
φ2 double precision = lat2 * rad;
Δφ double precision = (lat2 - lat1) * rad;
Δλ double precision = (lon2 - lon1) * rad;
a double precision = sin(Δφ / 2) * sin(Δφ / 2) + cos(φ1) * cos(φ2) * sin(Δλ / 2) * sin(Δλ / 2);
c double precision = 2 * atan2(sqrt(a), sqrt(1 - a));
BEGIN RETURN R * c;

END $BODY$ LANGUAGE plpgsql VOLATILE COST 100;
