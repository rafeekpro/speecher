-- PostgreSQL initialization script for Speecher development
-- This script runs when the PostgreSQL container starts for the first time

-- Create test database if it doesn't exist
SELECT 'CREATE DATABASE speecher_test' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'speecher_test')\gexec

-- Switch to speecher_dev database (default database from environment)
\c speecher_dev;

-- Create any required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Switch to test database and add extensions there too
\c speecher_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Note: Tables will be created by FastAPI/SQLAlchemy migrations
-- This script only handles database-level setup