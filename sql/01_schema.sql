-- 01_schema.sql
CREATE SCHEMA IF NOT EXISTS mart;

-- ========== FACT: APPLICATION ==========
DROP TABLE IF EXISTS mart.fact_application CASCADE;
CREATE TABLE mart.fact_application (
  sk_id_curr BIGINT PRIMARY KEY,
  target BOOLEAN,

  name_contract_type VARCHAR(50),
  amt_income_total DOUBLE PRECISION,
  amt_credit DOUBLE PRECISION,
  amt_annuity DOUBLE PRECISION,
  amt_goods_price DOUBLE PRECISION,

  days_birth INTEGER,
  days_employed INTEGER,

  flag_own_car BOOLEAN,
  flag_own_realty BOOLEAN,
  cnt_children INTEGER,

  region_population_relative DECIMAL(8,6),

  ext_source_1 DECIMAL(4,3),
  ext_source_2 DECIMAL(4,3),
  ext_source_3 DECIMAL(4,3),

 
  CONSTRAINT ck_fact_app_target CHECK (target IN (TRUE, FALSE) OR target IS NULL),
  CONSTRAINT ck_fact_app_amt_credit CHECK (amt_credit IS NULL OR amt_credit >= 0),
  CONSTRAINT ck_fact_app_amt_income CHECK (amt_income_total IS NULL OR amt_income_total >= 0),
  CONSTRAINT ck_fact_app_cnt_children CHECK (cnt_children IS NULL OR cnt_children >= 0),
  CONSTRAINT ck_fact_app_ext1 CHECK (ext_source_1 IS NULL OR (ext_source_1 >= 0 AND ext_source_1 <= 1)),
  CONSTRAINT ck_fact_app_ext2 CHECK (ext_source_2 IS NULL OR (ext_source_2 >= 0 AND ext_source_2 <= 1)),
  CONSTRAINT ck_fact_app_ext3 CHECK (ext_source_3 IS NULL OR (ext_source_3 >= 0 AND ext_source_3 <= 1))
);

-- ========== DIM: CUSTOMER ==========
DROP TABLE IF EXISTS mart.dim_customer CASCADE;
CREATE TABLE mart.dim_customer (
  sk_id_curr BIGINT PRIMARY KEY,

  code_gender VARCHAR(10),
  name_education_type VARCHAR(50),
  name_income_type VARCHAR(50),
  occupation_type VARCHAR(50),
  organization_type VARCHAR(50),
  name_family_status VARCHAR(50),
  name_housing_type VARCHAR(50),

  cnt_children INTEGER,
  region_population_relative DECIMAL(8,6),

  CONSTRAINT ck_dim_cnt_children CHECK (cnt_children IS NULL OR cnt_children >= 0),
  CONSTRAINT ck_dim_region_pop CHECK (region_population_relative IS NULL OR region_population_relative >= 0)
);

-- ========== FACT: PREVIOUS LOANS (AGG) ==========
DROP TABLE IF EXISTS mart.fact_previous_loans CASCADE;
CREATE TABLE mart.fact_previous_loans (
  sk_id_curr BIGINT PRIMARY KEY,

  prev_app_cnt INTEGER,
  prev_approved_cnt INTEGER,
  prev_refused_cnt INTEGER,
  prev_approved_rate DECIMAL(5,4),
  prev_amt_credit_mean DOUBLE PRECISION,
  prev_amt_credit_max DOUBLE PRECISION,
  prev_amt_annuity_mean DOUBLE PRECISION,
  prev_days_decision_min INTEGER,

  bureau_credit_cnt INTEGER,
  bureau_active_cnt INTEGER,
  bureau_closed_cnt INTEGER,
  bureau_sum_debt DOUBLE PRECISION,
  bureau_sum_overdue DOUBLE PRECISION,
  bureau_max_overdue DOUBLE PRECISION,
  bureau_credit_day_overdue_max INTEGER,

  inst_pay_cnt INTEGER,
  inst_late_cnt INTEGER,
  inst_late_rate DECIMAL(5,4),
  inst_days_late_mean DOUBLE PRECISION,
  inst_days_late_max DOUBLE PRECISION,
  inst_amt_payment_sum DOUBLE PRECISION,
  inst_payment_ratio_mean DECIMAL(6,4),

  CONSTRAINT ck_prev_rates CHECK (
    (prev_approved_rate IS NULL OR (prev_approved_rate >= 0 AND prev_approved_rate <= 1)) AND
    (inst_late_rate IS NULL OR (inst_late_rate >= 0 AND inst_late_rate <= 1)) AND
    (inst_payment_ratio_mean IS NULL OR inst_payment_ratio_mean >= 0)
  )
);

