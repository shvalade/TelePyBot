DELETE FROM test_table1 WHERE 


SELECT * FROM test_table1 ORDER BY RANDOM() LIMIT 1



SELECT * FROM test_table1
  WHERE _ROWID_ >= (abs(random()) % (SELECT max(_ROWID_) FROM test_table1))
  LIMIT 1;