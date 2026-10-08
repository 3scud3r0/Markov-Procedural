-- Generated SQLite query. Bind integer inputs within +/-1,000,000.
WITH
inputs AS (SELECT :x AS x, :y AS y),
proc_000_s1 AS (SELECT x AS x, y AS y, (((-7 * 3) + (y - x)) * 2) AS value FROM inputs),
proc_000_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 10)) THEN (value + (0 + 3)) ELSE (value - 2) END) AS value FROM proc_000_s1),
proc_000_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s2),
proc_000_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 10)) THEN (value + (1 + 3)) ELSE (value - 2) END) AS value FROM proc_000_s3),
proc_000_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s4),
proc_000_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 10)) THEN (value + (2 + 3)) ELSE (value - 2) END) AS value FROM proc_000_s5),
proc_000_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s6),
proc_000_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 10)) THEN (value + (3 + 3)) ELSE (value - 2) END) AS value FROM proc_000_s7),
proc_000_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s8),
proc_000_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 10)) THEN (value + (4 + 3)) ELSE (value - 2) END) AS value FROM proc_000_s9),
proc_000_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s10),
proc_001_s1 AS (SELECT x AS x, y AS y, (((y - 5) - (y + x)) + ((x * 8) - (y + x))) AS value FROM inputs),
proc_001_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 12)) THEN (value + (0 + 4)) ELSE (value - 3) END) AS value FROM proc_001_s1),
proc_001_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s2),
proc_001_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 12)) THEN (value + (1 + 4)) ELSE (value - 3) END) AS value FROM proc_001_s3),
proc_001_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s4),
proc_001_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 12)) THEN (value + (2 + 4)) ELSE (value - 3) END) AS value FROM proc_001_s5),
proc_001_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s6),
proc_001_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 12)) THEN (value + (3 + 4)) ELSE (value - 3) END) AS value FROM proc_001_s7),
proc_001_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s8),
proc_001_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 12)) THEN (value + (4 + 4)) ELSE (value - 3) END) AS value FROM proc_001_s9),
proc_001_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s10),
proc_002_s1 AS (SELECT x AS x, y AS y, (((y - -3) + (y * 2)) - ((y * 5) * 3)) AS value FROM inputs),
proc_002_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 3)) THEN (value + (0 + 1)) ELSE (value - 6) END) AS value FROM proc_002_s1),
proc_002_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s2),
proc_002_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 3)) THEN (value + (1 + 1)) ELSE (value - 6) END) AS value FROM proc_002_s3),
proc_002_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s4),
proc_002_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 3)) THEN (value + (2 + 1)) ELSE (value - 6) END) AS value FROM proc_002_s5),
proc_002_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s6),
proc_002_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 3)) THEN (value + (3 + 1)) ELSE (value - 6) END) AS value FROM proc_002_s7),
proc_002_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s8),
proc_002_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + 3)) THEN (value + (4 + 1)) ELSE (value - 6) END) AS value FROM proc_002_s9),
proc_002_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s10),
proc_003_s1 AS (SELECT x AS x, y AS y, (((-4 + x) - (x * 9)) * 3) AS value FROM inputs),
proc_003_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -9)) THEN (value + (0 + 4)) ELSE (value - 4) END) AS value FROM proc_003_s1),
proc_003_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s2),
proc_003_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -9)) THEN (value + (1 + 4)) ELSE (value - 4) END) AS value FROM proc_003_s3),
proc_003_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s4),
proc_003_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -9)) THEN (value + (2 + 4)) ELSE (value - 4) END) AS value FROM proc_003_s5),
proc_003_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s6),
proc_003_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -9)) THEN (value + (3 + 4)) ELSE (value - 4) END) AS value FROM proc_003_s7),
proc_003_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s8),
proc_003_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + -9)) THEN (value + (4 + 4)) ELSE (value - 4) END) AS value FROM proc_003_s9),
proc_003_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s10)
SELECT 'proc_000' AS function_name, value AS result FROM proc_000_s11
UNION ALL
SELECT 'proc_001' AS function_name, value AS result FROM proc_001_s11
UNION ALL
SELECT 'proc_002' AS function_name, value AS result FROM proc_002_s11
UNION ALL
SELECT 'proc_003' AS function_name, value AS result FROM proc_003_s11;
