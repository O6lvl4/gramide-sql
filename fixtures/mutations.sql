BEGIN IMMEDIATE TRANSACTION;
INSERT INTO users(email, display_name) VALUES
  ('demo@example.test', '日本語'), ('other@example.test', 'O''Brien')
ON CONFLICT(email) DO UPDATE SET display_name = 'updated'
RETURNING id, email;
UPDATE users SET active = 0 WHERE id IN (SELECT user_id FROM visits);
DELETE FROM visits WHERE duration BETWEEN 0 AND 1 RETURNING *;
ALTER TABLE users ADD COLUMN score REAL DEFAULT 0;
SAVEPOINT checkpoint;
ROLLBACK TO SAVEPOINT checkpoint;
RELEASE checkpoint;
COMMIT;
