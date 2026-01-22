-- =====================================================
-- Enriched fact: previous loans + bureau information
-- =====================================================

CREATE OR REPLACE VIEW mart.fact_previous_loans_enriched AS
SELECT
  fp.sk_id_curr,

  -- previous loan aggregates
  fp.prev_app_cnt,
  fp.prev_approved_cnt,
  fp.prev_refused_cnt,
  fp.prev_approved_rate,
  fp.prev_amt_credit_mean,
  fp.prev_amt_credit_max,
  fp.prev_amt_annuity_mean,
  fp.prev_days_decision_min,

  -- bureau aggregates
  b.bureau_credit_cnt,
  b.bureau_active_cnt,
  b.bureau_closed_cnt,
  b.bureau_sum_debt,
  b.bureau_sum_overdue,
  b.bureau_max_overdue

FROM mart.fact_previous_loans fp
LEFT JOIN mart.stg_bureau_agg b
  ON fp.sk_id_curr = b.sk_id_curr;

CREATE OR REPLACE VIEW mart.vw_credit_risk_summary AS
SELECT
  sk_id_curr,
  bureau_credit_cnt,
  bureau_sum_debt,
  bureau_max_overdue
FROM mart.fact_previous_loans_enriched;

-- =========================================================
-- Enriched fact: previous loans + bureau + installments
-- =========================================================

CREATE OR REPLACE VIEW mart.fact_previous_loans_enriched AS
SELECT
    fp.sk_id_curr,

    -- ===== previous application aggregates =====
    fp.prev_app_cnt,
    fp.prev_approved_cnt,
    fp.prev_refused_cnt,
    fp.prev_approved_rate,
    fp.prev_amt_credit_mean,
    fp.prev_amt_credit_max,
    fp.prev_amt_annuity_mean,
    fp.prev_days_decision_min,

    -- ===== bureau aggregates =====
    b.bureau_credit_cnt,
    b.bureau_active_cnt,
    b.bureau_closed_cnt,
    b.bureau_sum_debt,
    b.bureau_sum_overdue,
    b.bureau_max_overdue,

    -- ===== installments (repayment behavior) =====
    i.inst_pay_cnt,
    i.inst_late_cnt,
    i.inst_late_rate,
    i.inst_days_late_mean,
    i.inst_days_late_max,
    i.inst_amt_payment_sum,
    i.inst_amt_instalment_sum,
    i.inst_payment_ratio_mean

FROM mart.fact_previous_loans fp
LEFT JOIN mart.stg_bureau_agg b
    ON fp.sk_id_curr = b.sk_id_curr
LEFT JOIN mart.stg_installments_agg i
    ON fp.sk_id_curr = i.sk_id_curr;


-- =========================================================
-- Customer risk profile view (1 row per SK_ID_CURR)
-- Assumes data is already cleaned and placeholders handled.
-- Includes: demographics + application + engineered ratios
--          + risk bands + simple risk score + tier
-- =========================================================

CREATE OR REPLACE VIEW mart.vw_customer_risk_profile AS
WITH base AS (
  SELECT
    fa.sk_id_curr,

    -- label / product
    fa.target,
    fa.name_contract_type,

    -- demographics (dim)
    dc.code_gender,
    dc.name_education_type,
    dc.name_income_type,
    dc.occupation_type,
    dc.organization_type,
    dc.name_family_status,
    dc.name_housing_type,

    -- application amounts
    fa.amt_income_total,
    fa.amt_credit,
    fa.amt_annuity,
    fa.amt_goods_price,

    -- ownership
    fa.flag_own_car,
    fa.flag_own_realty,

    -- household / region
    fa.cnt_children,
    fa.region_population_relative,

    -- age / employment (days_* are typically negative in this dataset)
    ROUND(ABS(fa.days_birth) / 365.25, 1) AS age_years,
    ROUND(ABS(fa.days_employed) / 365.25, 1) AS employed_years,

    -- external scores
    fa.ext_source_1,
    fa.ext_source_2,
    fa.ext_source_3,
    (fa.ext_source_1 + fa.ext_source_2 + fa.ext_source_3) / 3.0 AS ext_source_mean,

    -- engineered ratios (safe guards)
    CASE
      WHEN fa.amt_income_total > 0 THEN fa.amt_credit / fa.amt_income_total
      ELSE NULL
    END AS loan_to_income,

    CASE
      WHEN fa.amt_income_total > 0 THEN fa.amt_annuity / fa.amt_income_total
      ELSE NULL
    END AS annuity_to_income,

    CASE
      WHEN fa.amt_credit > 0 THEN fa.amt_annuity / fa.amt_credit
      ELSE NULL
    END AS annuity_to_credit

  FROM mart.fact_application fa
  LEFT JOIN mart.dim_customer dc
    ON dc.sk_id_curr = fa.sk_id_curr
),
scored AS (
  SELECT
    b.*,

    -- bands (BI-friendly)
    CASE
      WHEN b.age_years IS NULL THEN NULL
      WHEN b.age_years < 30 THEN 'under_30'
      WHEN b.age_years < 45 THEN '30_44'
      WHEN b.age_years < 60 THEN '45_59'
      ELSE '60_plus'
    END AS age_band,

    CASE
      WHEN b.loan_to_income IS NULL THEN NULL
      WHEN b.loan_to_income >= 6 THEN 'very_high'
      WHEN b.loan_to_income >= 4 THEN 'high'
      WHEN b.loan_to_income >= 2 THEN 'medium'
      ELSE 'low'
    END AS lti_band,

    CASE
      WHEN b.annuity_to_income IS NULL THEN NULL
      WHEN b.annuity_to_income >= 0.5 THEN 'very_high'
      WHEN b.annuity_to_income >= 0.35 THEN 'high'
      WHEN b.annuity_to_income >= 0.2 THEN 'medium'
      ELSE 'low'
    END AS dti_band,

    CASE
      WHEN b.ext_source_mean IS NULL THEN NULL
      WHEN b.ext_source_mean >= 0.8 THEN 'best'
      WHEN b.ext_source_mean >= 0.6 THEN 'good'
      WHEN b.ext_source_mean >= 0.4 THEN 'medium'
      ELSE 'weak'
    END AS ext_band,

    -- simple risk score (dashboard-friendly; not a model)
    (
      COALESCE(1 - b.ext_source_mean, 0) * 0.6
      + COALESCE(b.annuity_to_income, 0) * 0.25
      + COALESCE(b.loan_to_income, 0) * 0.15
    ) AS risk_score_simple

  FROM base b
)
SELECT
  s.*,
  CASE
    WHEN s.risk_score_simple IS NULL THEN NULL
    WHEN s.risk_score_simple >= 1.0 THEN 'high'
    WHEN s.risk_score_simple >= 0.6 THEN 'medium'
    ELSE 'low'
  END AS risk_tier
FROM scored s;

