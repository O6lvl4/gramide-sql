-- UTF-8: 日本語 schema and café data
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT DEFAULT 'anonymous',
  active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);
CREATE TABLE visits (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  happened_at TEXT DEFAULT CURRENT_TIMESTAMP,
  duration REAL CHECK (duration >= 0),
  PRIMARY KEY (user_id, happened_at)
);
CREATE UNIQUE INDEX users_email ON users(email COLLATE nocase);
CREATE VIEW active_users AS SELECT id, email FROM users WHERE active = 1;
