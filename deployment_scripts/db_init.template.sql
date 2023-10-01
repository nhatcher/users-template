CREATE DATABASE <DATABASE_NAME>;
CREATE USER <DATABASE_USER> WITH PASSWORD '<DATABASE_PASSWORD>';
ALTER ROLE <DATABASE_USER> SET client_encoding TO 'utf8';
ALTER ROLE <DATABASE_USER> SET default_transaction_isolation TO 'read committed';
ALTER ROLE <DATABASE_USER> SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE <DATABASE_NAME> TO <DATABASE_USER>;