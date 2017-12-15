DROP FUNCTION IF EXISTS speedup(t1 NUMERIC, t2 NUMERIC, OUT speedup NUMERIC);
CREATE OR REPLACE FUNCTION speedup(t1 NUMERIC, t2 NUMERIC, OUT speedup NUMERIC) as $$
BEGIN
  IF t1 >= t2 THEN
    speedup := t1 / t2;
  ELSE
    speedup := (-1)*(t2/t1);
  END IF;
EXCEPTION
  WHEN DIVISION_BY_ZERO  THEN -- ignore.
END
$$ language plpgsql;
