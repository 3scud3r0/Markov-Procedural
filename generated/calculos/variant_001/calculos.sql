-- Generated SQLite query. Bind integer inputs within +/-1,000,000.
WITH
inputs AS (SELECT :x AS x, :y AS y),
proc_000_s1 AS (SELECT x AS x, y AS y, (((x - 1) - (8 - x)) - ((y - x) * 3)) AS value FROM inputs),
proc_000_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 20)) THEN (value + (0 + 8)) ELSE (value - 7) END) AS value FROM proc_000_s1),
proc_000_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s2),
proc_000_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 20)) THEN (value + (1 + 8)) ELSE (value - 7) END) AS value FROM proc_000_s3),
proc_000_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s4),
proc_000_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 20)) THEN (value + (2 + 8)) ELSE (value - 7) END) AS value FROM proc_000_s5),
proc_000_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s6),
proc_000_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 20)) THEN (value + (3 + 8)) ELSE (value - 7) END) AS value FROM proc_000_s7),
proc_000_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s8),
proc_000_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 20)) THEN (value + (4 + 8)) ELSE (value - 7) END) AS value FROM proc_000_s9),
proc_000_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s10),
proc_001_s1 AS (SELECT x AS x, y AS y, (((y - x) + (x - x)) * 2) AS value FROM inputs),
proc_001_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -11)) THEN (value + (0 + 9)) ELSE (value - 2) END) AS value FROM proc_001_s1),
proc_001_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s2),
proc_001_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -11)) THEN (value + (1 + 9)) ELSE (value - 2) END) AS value FROM proc_001_s3),
proc_001_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s4),
proc_001_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -11)) THEN (value + (2 + 9)) ELSE (value - 2) END) AS value FROM proc_001_s5),
proc_001_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s6),
proc_001_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -11)) THEN (value + (3 + 9)) ELSE (value - 2) END) AS value FROM proc_001_s7),
proc_001_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s8),
proc_001_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -11)) THEN (value + (4 + 9)) ELSE (value - 2) END) AS value FROM proc_001_s9),
proc_001_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s10),
proc_002_s1 AS (SELECT x AS x, y AS y, (((y + 9) + (x * 3)) * 1) AS value FROM inputs),
proc_002_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 7)) THEN (value + (0 + 9)) ELSE (value - 4) END) AS value FROM proc_002_s1),
proc_002_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s2),
proc_002_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 7)) THEN (value + (1 + 9)) ELSE (value - 4) END) AS value FROM proc_002_s3),
proc_002_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s4),
proc_002_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 7)) THEN (value + (2 + 9)) ELSE (value - 4) END) AS value FROM proc_002_s5),
proc_002_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s6),
proc_002_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 7)) THEN (value + (3 + 9)) ELSE (value - 4) END) AS value FROM proc_002_s7),
proc_002_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s8),
proc_002_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 7)) THEN (value + (4 + 9)) ELSE (value - 4) END) AS value FROM proc_002_s9),
proc_002_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s10),
proc_003_s1 AS (SELECT x AS x, y AS y, (((x + x) - (y * 9)) * 9) AS value FROM inputs),
proc_003_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -8)) THEN (value + (0 + 2)) ELSE (value - 4) END) AS value FROM proc_003_s1),
proc_003_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s2),
proc_003_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -8)) THEN (value + (1 + 2)) ELSE (value - 4) END) AS value FROM proc_003_s3),
proc_003_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s4),
proc_003_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -8)) THEN (value + (2 + 2)) ELSE (value - 4) END) AS value FROM proc_003_s5),
proc_003_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s6),
proc_003_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -8)) THEN (value + (3 + 2)) ELSE (value - 4) END) AS value FROM proc_003_s7),
proc_003_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s8),
proc_003_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -8)) THEN (value + (4 + 2)) ELSE (value - 4) END) AS value FROM proc_003_s9),
proc_003_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s10)
SELECT 'proc_000' AS function_name, value AS result FROM proc_000_s11
UNION ALL
SELECT 'proc_001' AS function_name, value AS result FROM proc_001_s11
UNION ALL
SELECT 'proc_002' AS function_name, value AS result FROM proc_002_s11
UNION ALL
SELECT 'proc_003' AS function_name, value AS result FROM proc_003_s11;
