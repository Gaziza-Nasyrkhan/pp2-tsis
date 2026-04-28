DROP TABLE IF EXISTS phones;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS groups;

CREATE TABLE groups(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE contacts(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    phone VARCHAR(100), 
    email VARCHAR(100),
    birthday DATE,
    group_id INTEGER REFERENCES groups(id)
);

CREATE TABLE phones(
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK(type IN ('home', 'work', 'mobile'))
);

INSERT INTO groups(name) VALUES 
    ('family'),
    ('work'),
    ('friend'),
    ('other');