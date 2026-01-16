-- Supabase Setup Script for Sports Commentary Analyzer
-- This script can be used to verify the database schema after Alembic migrations
-- or to manually create tables if needed.

-- Note: Alembic migrations (alembic upgrade head) will create these tables automatically.
-- This file is provided for reference and manual verification.

-- Enable UUID extension (usually enabled by default in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify tables exist (run after alembic upgrade head)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('transcripts', 'players', 'analysis_results', 'alembic_version');

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'transcripts'
ORDER BY ordinal_position;

-- Row Level Security (Optional - Enable if you want additional security)
-- Uncomment these lines if you want to enable RLS

-- ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE players ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (adjust as needed for your security requirements)
-- CREATE POLICY "Allow all operations" ON transcripts FOR ALL USING (true);
-- CREATE POLICY "Allow all operations" ON players FOR ALL USING (true);
-- CREATE POLICY "Allow all operations" ON analysis_results FOR ALL USING (true);

-- Useful queries for monitoring

-- Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Check table sizes
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Check connection count
SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();
