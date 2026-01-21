-- 03_validate.sql

-- 0) row counts 
SELECT 'fact_application' AS table, COUNT(*) AS rows FROM mart.fact_application
UNION ALL SELECT 'dim_customer', COUNT(*) FROM mart.dim_customer
UNION ALL SELECT 'fact_previous_loans', COUNT(*) FROM mart.fact_previous_loans;


-- 1) PK uniqueness: fact_application
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sk_id_curr) AS distinct_pk,
  COUNT(*) - COUNT(DISTINCT sk_id_curr) AS dup_pk_cnt
FROM mart.fact_application;


-- 1b) PK uniqueness: dim_customer
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sk_id_curr) AS distinct_pk,
  COUNT(*) - COUNT(DISTINCT sk_id_curr) AS dup_pk_cnt
FROM mart.dim_customer;


-- 1c) Uniqueness: fact_previous_loans 
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sk_id_curr) AS distinct_key,
  COUNT(*) - COUNT(DISTINCT sk_id_curr) AS dup_key_cnt
FROM mart.fact_previous_loans;


-- 2) Join explosion check: if dup_key_cnt > 0, joined_rows > app_rows
SELECT
  (SELECT COUNT(*) FROM mart.fact_application) AS app_rows,
  (SELECT COUNT(*) FROM mart.fact_application fa
   LEFT JOIN mart.fact_previous_loans fp USING (sk_id_curr)) AS joined_rows;


-- 3) fact_application -> dim_customer match + orphans
SELECT
  COUNT(*) AS app_rows,
  COUNT(dc.sk_id_curr) AS matched_dim_rows,
  SUM((dc.sk_id_curr IS NULL)::int) AS orphan_app_to_dim
FROM mart.fact_application fa
LEFT JOIN mart.dim_customer dc USING (sk_id_curr);


-- 4) fact_application -> fact_previous_loans match + missing prev for app
SELECT
  COUNT(*) AS app_rows,
  COUNT(fp.sk_id_curr) AS matched_prev_rows,
  SUM((fp.sk_id_curr IS NULL)::int) AS missing_prev_for_app
FROM mart.fact_application fa
LEFT JOIN mart.fact_previous_loans fp USING (sk_id_curr);


-- 5) reverse orphan: prev rows not found in application 
SELECT
  COUNT(*) AS orphan_prev_to_app
FROM mart.fact_previous_loans fp
LEFT JOIN mart.fact_application fa USING (sk_id_curr)
WHERE fa.sk_id_curr IS NULL;
