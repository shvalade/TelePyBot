-- test_table definition

CREATE TABLE "test_table1" (
	id INTEGER PRIMARY KEY,
	link TEXT DEFAULT 0 NOT NULL,
	create_time TEXT NOT NULL,
	request_time TEXT DEFAULT 0 NOT NULL);