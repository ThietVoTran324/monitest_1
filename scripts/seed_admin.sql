-- Bootstrap first admin (Sprint6). Run once against the users table.
-- Example:
--   docker compose exec -T postgres psql -U moni -d moni -f - < scripts/seed_admin.sql
-- Replace the email with an existing verified user.

UPDATE users
SET is_admin = true
WHERE email = 'admin@example.com';
