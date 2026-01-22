SELECT * FROM mart.fact_application LIMIT5;

SELECT * FROM mart.fact_previous_loans LIMIT5;

SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'mart'
  AND table_name = 'fact_previous_loans';

-- Risk by previous refusal rate
WITH joined AS (
  SELECT
    fa.sk_id_curr,
    fa.target,
    fp.prev_app_cnt,
    fp.prev_refused_cnt,
    CASE
      WHEN fp.prev_app_cnt IS NULL OR fp.prev_app_cnt = 0 THEN NULL
      ELSE fp.prev_refused_cnt::numeric / fp.prev_app_cnt
    END AS prev_refuse_rate
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans fp
    ON fa.sk_id_curr = fp.sk_id_curr
)
SELECT
  CASE
    WHEN prev_refuse_rate IS NULL THEN 'no_history'
    WHEN prev_refuse_rate = 0 THEN '0%'
    WHEN prev_refuse_rate <= 0.25 THEN '(0, 25%]'
    WHEN prev_refuse_rate <= 0.50 THEN '(25, 50%]'
    WHEN prev_refuse_rate <= 0.75 THEN '(50, 75%]'
    ELSE '(75, 100%]'
  END AS prev_refuse_rate_bucket,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM joined
GROUP by 1
ORDER BY n_apps DESC;

-- Risk by bureau debt pressure
WITH base AS(
  SELECT
    fa.sk_id_curr,
    fa.target,
    fp.bureau_sum_debt
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans_enriched fp
    ON fa.sk_id_curr = fp.sk_id_curr
)
SELECT
  CASE
    WHEN bureau_sum_debt IS NULL THEN 'no_bureau_record'
    WHEN bureau_sum_debt = 0 THEN '0'
    WHEN bureau_sum_debt < 50000 THEN '<50k'
    WHEN bureau_sum_debt < 200000 THEN '50k-200k'
    WHEN bureau_sum_debt < 500000 THEN '200k-500k'
    ELSE '500k+'
  END AS debt_bucket,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM base
GROUP BY 1
ORDER BY n_apps DESC;

-- Risk by bureau max overdue (bureau_max_overdue)
WITH base AS (
  SELECT
    fa.sk_id_curr,
    fa.target,
    fp.bureau_max_overdue
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans_enriched fp
    ON fa.sk_id_curr = fp.sk_id_curr
)
SELECT
  CASE
    WHEN bureau_max_overdue IS NULL THEN 'no_bureau_record'
    WHEN bureau_max_overdue = 0 THEN '0'
    WHEN bureau_max_overdue < 1000 THEN '(0, 1k)'
    WHEN bureau_max_overdue < 5000 THEN '[1k, 5k)'
    WHEN bureau_max_overdue < 20000 THEN '[5k, 20k)'
    ELSE '20k+'
  END AS max_overdue_bucket,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM base
GROUP BY 1
ORDER BY n_apps DESC;

-- Risk by number of bureau credits (bureau_credit_cnt)
WITH base AS (
  SELECT
    fa.sk_id_curr,
    fa.target,
    fp.bureau_credit_cnt
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans_enriched fp
    ON fa.sk_id_curr = fp.sk_id_curr
)
SELECT
  CASE
    WHEN bureau_credit_cnt IS NULL THEN 'no_bureau_record'
    WHEN bureau_credit_cnt = 0 THEN '0'
    WHEN bureau_credit_cnt BETWEEN 1 AND 2 THEN '1-2'
    WHEN bureau_credit_cnt BETWEEN 3 AND 5 THEN '3-5'
    WHEN bureau_credit_cnt BETWEEN 6 AND 10 THEN '6-10'
    ELSE '10+'
  END AS credit_cnt_bucket,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM base
GROUP BY 1
ORDER BY n_apps DESC;

-- Repayment Punctuality vs Default Risk

WITH base AS (
  SELECT
    fa.sk_id_curr,
    fa.target,
    fp.inst_late_rate
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans_enriched fp
    ON fa.sk_id_curr = fp.sk_id_curr
)

SELECT
  CASE
    WHEN inst_late_rate IS NULL THEN 'no_history'
    WHEN inst_late_rate = 0 THEN 'never_late'
    WHEN inst_late_rate <= 0.1 THEN 'rarely_late'
    WHEN inst_late_rate <= 0.3 THEN 'sometimes_late'
    ELSE 'often_late'
  END AS late_behavior,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM base
GROUP BY 1
ORDER BY n_apps DESC;

-- Average Days of Payment Delay vs Default Risk
WITH base AS(
  SELECT
    fa.target,
    fp.inst_days_late_mean
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans_enriched fp
    ON fa.sk_id_curr = fp.sk_id_curr
)
SELECT
  CASE
    WHEN inst_days_late_mean IS NULL THEN 'no_history'
    WHEN inst_days_late_mean = 0 THEN 'on_time'
    WHEN inst_days_late_mean <= 5 THEN 'minor_delay'
    WHEN inst_days_late_mean <= 30 THEN 'moderate_delay'
    ELSE 'severe_delay'
  END AS delay_severity,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM base
GROUP BY 1
ORDER BY n_apps DESC;

-- Combined Credit Bureau Exposure and Repayment Behavior Analysis
WITH base AS (
  SELECT
    fa.target,
    fp.bureau_sum_debt,
    fp.inst_late_rate
  FROM mart.fact_application fa
  LEFT JOIN mart.fact_previous_loans_enriched fp
    ON fa.sk_id_curr = fp.sk_id_curr
)
SELECT
  CASE
    WHEN bureau_sum_debt IS NULL THEN 'no_bureau'
    WHEN bureau_sum_debt < 50000 THEN 'low_debt'
    WHEN bureau_sum_debt < 200000 THEN 'mid_debt'
    ELSE 'high_debt'
  END AS debt_level,
  CASE
    WHEN inst_late_rate = 0 THEN 'never_late'
    ELSE 'ever_late'
  END AS repayment_behavior,
  COUNT(*) AS n_apps,
  AVG(CASE WHEN target THEN 1.0 ELSE 0.0 END) AS default_rate
FROM base
GROUP BY 1, 2
ORDER BY default_rate DESC;


SELECT
  risk_tier,
  COUNT(*) AS customers,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY risk_tier
ORDER BY risk_tier;

SELECT
  lti_band,
  COUNT(*) AS cnt,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY lti_band
ORDER BY lti_band;

SELECT
  ext_band,
  COUNT(*) AS cnt,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY ext_band
ORDER BY ext_band;

SELECT
  risk_tier,
  age_band,
  COUNT(*) AS customers
FROM mart.vw_customer_risk_profile
GROUP BY risk_tier, age_band
ORDER BY risk_tier, age_band;

SELECT
  COUNT(*) AS total_apps,
  AVG(target::int) AS current_default_rate,
  AVG(CASE WHEN risk_tier <> 'high' THEN target::int END) AS default_rate_after_policy
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL;

SELECT
  AVG((ext_source_mean IS NULL)::int) AS ext_missing_rate
FROM mart.vw_customer_risk_profile;

-- income vs risk
SELECT
  name_income_type,
  COUNT(*) AS customers,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY name_income_type
ORDER BY default_rate DESC;

-- education vs risk
SELECT
  name_education_type,
  COUNT(*) AS customers,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY name_education_type
ORDER BY default_rate DESC;

-- family statu vs risk
SELECT
  CASE
    WHEN cnt_children = 0 THEN 'no_children'
    WHEN cnt_children <= 2 THEN '1_2_children'
    ELSE '3plus_children'
  END AS children_band,
  COUNT(*) AS customers,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY children_band
ORDER BY children_band;

-- occupation type vs risk
SELECT
  occupation_type,
  COUNT(*) AS customers,
  AVG(target::int) AS default_rate
FROM mart.vw_customer_risk_profile
WHERE target IS NOT NULL
GROUP BY occupation_type
HAVING COUNT(*) > 1000
ORDER BY default_rate DESC;