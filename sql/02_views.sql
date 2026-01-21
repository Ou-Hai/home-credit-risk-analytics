CREATE OR REPLACE VIEW mart.v_application_enriched AS
SELECT
  fa.*,

  -- age in years (1 decimal)
  ROUND(ABS(fa.days_birth) / 365.25, 1) AS age_years_calc,

  dc.code_gender,
  dc.name_education_type,
  dc.name_income_type,
  dc.occupation_type,
  dc.organization_type,
  dc.name_family_status,
  dc.name_housing_type,

  -- fact_previous_loans (exclude sk_id_curr to avoid duplicate column)
  fp.prev_app_cnt,
  fp.prev_approved_cnt,
  fp.prev_refused_cnt,
  fp.prev_approved_rate,
  fp.prev_amt_credit_mean,
  fp.prev_amt_credit_max,
  fp.prev_amt_annuity_mean,
  fp.prev_days_decision_min,

  fp.bureau_credit_cnt,
  fp.bureau_active_cnt,
  fp.bureau_closed_cnt,
  fp.bureau_sum_debt,
  fp.bureau_sum_overdue,
  fp.bureau_max_overdue,
  fp.bureau_credit_day_overdue_max,

  fp.inst_pay_cnt,
  fp.inst_late_cnt,
  fp.inst_late_rate,
  fp.inst_days_late_mean,
  fp.inst_days_late_max,
  fp.inst_amt_payment_sum,
  fp.inst_payment_ratio_mean

FROM mart.fact_application fa
LEFT JOIN mart.dim_customer dc USING (sk_id_curr)
LEFT JOIN mart.fact_previous_loans fp USING (sk_id_curr);

CREATE OR REPLACE VIEW mart.v_kpi_segment AS
SELECT
  fa.name_contract_type,
  dc.name_education_type,
  COUNT(*) AS applications,
  AVG(fa.target::int) AS default_rate,
  AVG(fa.amt_credit) AS avg_amt_credit
FROM mart.fact_application fa
LEFT JOIN mart.dim_customer dc USING (sk_id_curr)
GROUP BY 1,2;