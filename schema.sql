CREATE TABLE atoms (
    atom_id SERIAL PRIMARY KEY,
    atom_name VARCHAR(100) NOT NULL,
);

INSERT INTO atoms (atom_name) VALUES ('hydrogen');

CREATE TABLE sensor_types (
    sensor_type_id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(100) NOT NULL
);

INSERT INTO sensor_types (sensor_name) VALUES ('temperature');

CREATE TABLE sensors (
    sensor_id SERIAL PRIMARY KEY,
    atom_id INTEGER REFERENCES atoms(atom_id) ON DELETE CASCADE ON UPDATE CASCADE,
    sensor_type INTEGER REFERENCES sensor_type(sensor_type_id) ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO sensors (atom_id, sensor_type) VALUES (1, 1);

CREATE TABLE raw_data (
    dp_id SERIAL PRIMARY KEY,
    atom_id INTEGER REFERENCES atoms(atom_id) ON DELETE CASCADE ON UPDATE CASCADE,
    sensor_id INTEGER REFERENCES sensors(sensor_id) ON DELETE CASECADE ON UPDATE CASCADE,
    dt_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    value REAL NOT NULL
);
