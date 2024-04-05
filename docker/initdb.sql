CREATE ROLE be;
CREATE DATABASE IF NOT EXISTS backendtes;
GRANT ALL PRIVILEGES ON backendtes TO be;
CREATE SCHEMA IF NOT EXISTS be_tes;
CREATE TABLE IF NOT EXISTS be_tes.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR,
    password VARCHAR,
    email VARCHAR,
    is_super VARCHAR,
    created_at VARCHAR,
    last_login VARCHAR,
);