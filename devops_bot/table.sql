CREATE USER repl_user REPLICATION PASSWORD 'P@ssw0rd';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE email (ID SERIAL PRIMARY KEY, emailname VARCHAR (100) NOT NULL);
CREATE TABLE numberPhone (ID SERIAL PRIMARY KEY, numberphone VARCHAR (100) NOT NULL);

