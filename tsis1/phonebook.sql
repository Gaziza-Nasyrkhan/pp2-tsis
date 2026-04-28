DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS groups CASCADE;
DROP TABLE IF EXISTS phones CASCADE;
DROP FUNCTION IF EXISTS get_contacts_paginated(integer, integer);
DROP PROCEDURE IF EXISTS deleting_contacts(VARCHAR, VARCHAR);  

CREATE TABLE contacts(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(100)
);

CREATE TABLE groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

ALTER TABLE contacts
    ADD COLUMN email    VARCHAR(100),
    ADD COLUMN birthday DATE,
    ADD COLUMN group_id INTEGER REFERENCES groups(id);

CREATE TABLE phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20)  NOT NULL,
    type       VARCHAR(10)  CHECK (type IN ('home', 'work', 'mobile'))
);

INSERT INTO groups(name) VALUES ('family'),('work'),('friend'),('other');

CREATE OR REPLACE FUNCTION get_contacts_by_patterns(p text)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT c.name, c.phone FROM contacts c
        WHERE c.name ILIKE '%' || p || '%'
        OR c.phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR, p_email VARCHAR, p_birthday DATE, p_group_id INT DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN 
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone, email, birthday, group_id) VALUES(p_name, p_phone, p_email, p_birthday, p_group_id);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_new_users(names VARCHAR[], phones VARCHAR[], emails VARCHAR[], birthdays DATE[], groups_id INT[] DEFAULT NULL)
LANGUAGE plpgsql AS $$
DECLARE 
    i INT;
    invalid_data TEXT[] := ARRAY[]::TEXT[];
BEGIN
    FOR I IN 1..array_length(names, 1) LOOP
        IF phones[i] ~'^\d+$' THEN
            CALL upsert_contact(names[i], phones[i], emails[i], birthdays[i], groups_id[i]);
        ELSE
            invalid_data := array_append(invalid_data, names[i] || ':' || phones[i]);
        END IF;
    END LOOP;

    IF array_length(invalid_data, 1) IS NOT NULL THEN
        RAISE NOTICE 'Invalid data: %', array_to_string(invalid_data, ',');
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR, email VARCHAR, birthday DATE, group_id INT) AS $$
BEGIN
    RETURN QUERY 
    SELECT c.id, c.name, c.phone, c.email, c.birthday, c.group_id 
    FROM contacts c
    ORDER BY id 
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE deleting_contacts(p_name VARCHAR DEFAULT NULL, p_phone VARCHAR DEFAULT NULL, p_email VARCHAR DEFAULT NULL, p_birthday DATE DEFAULT NULL, p_group_id INT DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM contacts WHERE name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM contacts WHERE phone = p_phone;
    ELSE
        RAISE NOTICE 'No name or phone provided!';
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    INSERT INTO phones(contact_id, phone, type) VALUES (v_contact_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE 
    v_group_id INT;
BEGIN
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN 
        INSERT INTO groups(name) VALUES(p_group_name) RETURNING id INTO v_group_id;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE name = p_contact_name;
END;
$$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR, email VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT c.id, c.name, c.phone, c.email
    FROM contacts c
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
    OR c.email ILIKE '%' || p_query || '%'
    OR p.phone ILIKE '%' || p_query || '%';
END;
$$ LANGUAGE plpgsql;


CALL upsert_contact('Madina', '87767321438', 'turgynbekovamadina@gmail.com', '2008-04-10');
CALL upsert_contact('Merey', '87765321438', 'turgynbekovamerey@gmail.com', '2004-03-20', 1);
CALL upsert_contact('Mingyu', '87956143855', 'kim.mingyu@gmail.com', '1997-04-06', 4);
CALL upsert_contact('Mdin', '821438', 'gvfhsdhb@gmail.com', '1852-02-25');
--pagination
SELECT get_contacts_paginated(1, 2);
--search by patterns
SELECT get_contacts_by_patterns('776732');
--insert with array
CALL insert_new_users(ARRAY['fghj', 'ghjk', 'ghjkjk'], ARRAY['74185','85296','8525'], ARRAY['cvghgfygf@gmail.com', 'hufhurfhuhu@gmail.com', 'qwerty@gmail.com'], ARRAY['2008-04-11', '1976-02-14', '2024-07-18']::DATE[]);
SELECT * FROM contacts;
-- deleting
CALL deleting_contacts(p_name := 'Mdin');
--add phone to phones
CALL add_phone('Merey', '87767361498', 'work');
--move to group
CALL move_to_group('Merey', 'family');
--search contacts 
SELECT * FROM search_contacts('8776');

SELECT * FROM contacts;