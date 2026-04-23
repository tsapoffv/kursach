CREATE DATABASE schedule_db;
CREATE USER schedule_user WITH PASSWORD 'my_secret_pw';
GRANT ALL ON SCHEMA public TO schedule_user;
ALTER USER schedule_user WITH SUPERUSER;