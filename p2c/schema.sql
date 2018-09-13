DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS pick;

--user is a pparently a reserved word so i changed it to people
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  score INTEGER NOT NULL DEFAULT 0,
  password TEXT NOT NULL
);

CREATE TABLE pick (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL, 
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  player TEXT NOT NULL,
  click BIT DEFAULT NULL
);
