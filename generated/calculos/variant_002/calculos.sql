-- Generated SQLite query. Bind integer inputs within +/-1,000,000.
WITH
inputs AS (SELECT :x AS x, :y AS y),
proc_000_s1 AS (SELECT x AS x, y AS y, (((4 - -4) + (1 - x)) + ((x * 3) + (3 - 0))) AS value FROM inputs),
proc_000_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -14)) THEN (value + (0 + 5)) ELSE (value - 9) END) AS value FROM proc_000_s1),
proc_000_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s2),
proc_000_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -14)) THEN (value + (1 + 5)) ELSE (value - 9) END) AS value FROM proc_000_s3),
proc_000_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s4),
proc_000_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -14)) THEN (value + (2 + 5)) ELSE (value - 9) END) AS value FROM proc_000_s5),
proc_000_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s6),
proc_000_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -14)) THEN (value + (3 + 5)) ELSE (value - 9) END) AS value FROM proc_000_s7),
proc_000_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s8),
proc_000_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -14)) THEN (value + (4 + 5)) ELSE (value - 9) END) AS value FROM proc_000_s9),
proc_000_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_000_s10),
proc_001_s1 AS (SELECT x AS x, y AS y, (((-8 - y) * 9) * 1) AS value FROM inputs),
proc_001_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -16)) THEN (value + (0 + 7)) ELSE (value - 9) END) AS value FROM proc_001_s1),
proc_001_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s2),
proc_001_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -16)) THEN (value + (1 + 7)) ELSE (value - 9) END) AS value FROM proc_001_s3),
proc_001_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s4),
proc_001_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -16)) THEN (value + (2 + 7)) ELSE (value - 9) END) AS value FROM proc_001_s5),
proc_001_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s6),
proc_001_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -16)) THEN (value + (3 + 7)) ELSE (value - 9) END) AS value FROM proc_001_s7),
proc_001_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s8),
proc_001_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value > (x + -16)) THEN (value + (4 + 7)) ELSE (value - 9) END) AS value FROM proc_001_s9),
proc_001_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_001_s10),
proc_002_s1 AS (SELECT x AS x, y AS y, (((x - 3) + (y + x)) + ((x * 4) + (y + y))) AS value FROM inputs),
proc_002_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 16)) THEN (value + (0 + 1)) ELSE (value - 7) END) AS value FROM proc_002_s1),
proc_002_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s2),
proc_002_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 16)) THEN (value + (1 + 1)) ELSE (value - 7) END) AS value FROM proc_002_s3),
proc_002_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s4),
proc_002_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 16)) THEN (value + (2 + 1)) ELSE (value - 7) END) AS value FROM proc_002_s5),
proc_002_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s6),
proc_002_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 16)) THEN (value + (3 + 1)) ELSE (value - 7) END) AS value FROM proc_002_s7),
proc_002_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s8),
proc_002_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value == (x + 16)) THEN (value + (4 + 1)) ELSE (value - 7) END) AS value FROM proc_002_s9),
proc_002_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_002_s10),
proc_003_s1 AS (SELECT x AS x, y AS y, (((4 + y) - (-2 + y)) - ((y * 9) * 4)) AS value FROM inputs),
proc_003_s2 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + 0)) THEN (value + (0 + 1)) ELSE (value - 5) END) AS value FROM proc_003_s1),
proc_003_s3 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s2),
proc_003_s4 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + 0)) THEN (value + (1 + 1)) ELSE (value - 5) END) AS value FROM proc_003_s3),
proc_003_s5 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s4),
proc_003_s6 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + 0)) THEN (value + (2 + 1)) ELSE (value - 5) END) AS value FROM proc_003_s5),
proc_003_s7 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s6),
proc_003_s8 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + 0)) THEN (value + (3 + 1)) ELSE (value - 5) END) AS value FROM proc_003_s7),
proc_003_s9 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s8),
proc_003_s10 AS (SELECT x AS x, y AS y, (CASE WHEN (value < (x + 0)) THEN (value + (4 + 1)) ELSE (value - 5) END) AS value FROM proc_003_s9),
proc_003_s11 AS (SELECT x AS x, y AS y, (value + y) AS value FROM proc_003_s10)
SELECT 'proc_000' AS function_name, value AS result FROM proc_000_s11
UNION ALL
SELECT 'proc_001' AS function_name, value AS result FROM proc_001_s11
UNION ALL
SELECT 'proc_002' AS function_name, value AS result FROM proc_002_s11
UNION ALL
SELECT 'proc_003' AS function_name, value AS result FROM proc_003_s11;
