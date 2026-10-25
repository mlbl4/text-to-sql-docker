-- =============================================================
-- 03_readonly_user.sql — Read-only role for the query service
-- The query service runs SQL written by a language model, so it
-- connects with a user that can ONLY read: even if the model
-- writes DROP TABLE or DELETE, PostgreSQL refuses it.
-- (Development password; in production it would come from a secret.)
-- =============================================================

CREATE ROLE readonly_user LOGIN PASSWORD 'readonly';

-- Can see the objects in the public schema...
GRANT USAGE ON SCHEMA public TO readonly_user;

-- ...and read the tables, but not modify them
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;