# Home Credit Risk Analytics

<p align="center">
  <img src="images/home_credit_logo.png" width="320">
</p>

## Project Overview
This project is an end-to-end data analytics and machine learning pipeline built on real-world financial credit data.
The objective is to support risk-based lending decisions by transforming raw, heterogeneous and noisy data into
actionable insights for financial institutions.

The project emphasizes not only predictive performance, but also data cleaning, data engineering,
economic interpretation and decision support.

---

## Business Context
Financial institutions face the challenge of assessing credit risk using incomplete, inconsistent
and high-dimensional data. Poor risk assessment may lead to higher default rates, financial losses
or unfair credit allocation.

This project aims to explore how data analytics and machine learning can be used to better understand
credit default risk and support more informed lending decisions.

---

## Business Questions
The project focuses on answering the following key business questions:

1. **Who is more likely to default on a loan?**  
   Identify borrower profiles with higher default probability based on demographic, financial
   and historical credit information.

2. **Which economic and financial variables are the most important drivers of default risk?**  
   Analyze the relative importance of income, employment, education, credit history and
   repayment behavior in explaining loan default.

3. **Are there systematic risk segments within the customer population?**  
   Investigate whether distinct risk groups exist and how they differ in terms of default rates
   and financial characteristics.

4. **How can historical credit behavior improve default prediction for new applicants?**  
   Evaluate how previous loans, repayments and credit bureau information contribute to more
   accurate risk assessment.

---

## Dataset
The project uses the **Home Credit Default Risk** dataset, provided by a real financial institution.
The dataset consists of multiple relational tables containing:

- Applicant demographic and financial information
- Historical credit bureau records
- Previous loan applications
- Installment and repayment histories

The data reflects real-world challenges such as missing values, inconsistent formats and varying
levels of granularity across tables.

---

## Project Scope
The project follows a complete data analytics pipeline:

- Data ingestion and exploration
- Data quality assessment and cleaning
- Feature engineering with economic interpretation
- Relational database design and ETL
- SQL-based analytical queries
- Machine learning modeling for default prediction
- Model evaluation and interpretation
- Dashboard for decision support
- API for model inference (optional, advanced)

---

## Tools & Technologies

### 🧑‍💻 Programming & Data Analysis
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-purple?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Scientific%20Computing-blue?logo=numpy&logoColor=white)

### 📊 Visualization & EDA
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-yellow)
![Seaborn](https://img.shields.io/badge/Seaborn-Statistical%20Plots-lightblue)

### 🧠 Machine Learning
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikitlearn&logoColor=white)

### 🗄️ Database & SQL
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql&logoColor=white)

### 📈 Business Intelligence
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-blue?logo=tableau)

### ⚙️ Data Engineering & Environment
![uv](https://img.shields.io/badge/uv-Environment%20Management-black)
![Docker](https://img.shields.io/badge/Docker-Containerization-blue?logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version%20Control-red?logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Code%20Hosting-black?logo=github)

### 🚀 API & Deployment (Optional)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI%20Server-green)

---

## Data Cleaning & Feature Preparation 

### Missing Values & Placeholders
- Performed a systematic missing value audit across all raw tables.
- Missing values are **not treated as random noise**, but categorized as:
  - Business non-applicability (e.g. housing-related features)
  - Implicit absence (e.g. no car → `OWN_CAR_AGE`)
  - Boundary or partial records (e.g. POS monthly data)
  - Technical placeholders (e.g. `365243` in previous applications)
- Strategy: **keep rows, preserve NaN, add indicator features when meaningful**.
- Technical placeholder values are explicitly converted to `NaN` to avoid misleading numerical interpretation.

---

### Numerical Outlier Handling
- **Age**: Converted from `DAYS_BIRTH` to `AGE_YEARS`; implausible values (<18 or >100) are flagged and set to `NaN`.
- **Income (`AMT_INCOME_TOTAL`)**:
  - Non-positive values are flagged as invalid.
  - Extreme values are clipped at the 1%–99% quantiles.
- **Credit amount (`AMT_CREDIT`)**:
  - Handled with the same strategy as income (flag + quantile clipping).

Principle: **clip instead of drop, flag instead of hide**.

---

### Train / Test Consistency
- Identical cleaning rules are applied to both training and test datasets.
- No test statistics are used during preprocessing.
- Cleaned datasets share consistent schemas and data types.

---

### Cleaned Data Outputs
At this stage, the following cleaned datasets are produced (Parquet format):
- `application_train_clean.parquet`
- `application_test_clean.parquet`
- `previous_application_clean.parquet`

These datasets serve as inputs for feature engineering, SQL modeling, and machine learning.

---

### Design Rationale (Short)
- Prefer **keep + flag** over row deletion.
- Treat missingness and anomalies as potential risk signals.
- Apply conservative, interpretable rules aligned with credit risk practice.

---

## Risk Analysis & SQL Insights 

Based on the analytical views in the `mart` schema, a series of SQL-based risk analyses were conducted to explore the relationship between historical behavior and default risk.

### Credit History & Bureau Risk
- **Previous refusal rate vs default risk**  
  Applicants are segmented by historical loan refusal rate to assess how repeated rejections correlate with higher default probability.
- **Credit bureau debt exposure**  
  Default rates are analyzed across total bureau debt buckets (from no bureau record to high outstanding debt).
- **Maximum overdue amount**  
  Risk is evaluated by the largest historical overdue amount reported in credit bureau data.
- **Number of bureau credits**  
  Applicants are grouped by the count of past bureau credits to capture credit depth vs risk.

---

### Repayment Behavior
- **Repayment punctuality**  
  Default risk is analyzed by installment late-rate buckets (never late → often late).
- **Average payment delay severity**  
  Mean days late are bucketed into severity bands (on-time, minor, moderate, severe delay).

These analyses highlight repayment discipline as a strong behavioral risk signal.

---

### Combined Risk Segmentation
- **Bureau exposure × repayment behavior**  
  Joint analysis of debt level and late-payment behavior to identify high-risk combinations.
- **Customer risk tiers**  
  Aggregated risk tiers are evaluated for customer count and default rate to support policy simulation.

---

### Demographic & Socioeconomic Risk Profiles
Using the customer risk profile view:
- **Income bands**
- **Education level**
- **Age groups**
- **Family structure (number of children)**
- **Occupation type**

Default rates are compared across segments to identify systematic risk patterns.

---

### Policy-Oriented Metrics
- Simulated impact of excluding high-risk tiers on overall default rate.
- Monitoring of external data availability (e.g. external score missing rate).

---

### Design Notes
- All analyses are performed via **reusable SQL views**, not ad-hoc queries.
- Segmentation is rule-based and interpretable.
- Results are suitable for dashboards, reporting, and downstream modeling.

This analytical layer bridges cleaned data, business insight, and credit risk decision support.

---

## Feature Engineering 

After data cleaning and analytical validation, a structured feature engineering process was applied to transform raw application- and bureau-level data into model-ready features with strong business interpretability.

---

### Feature Engineering Principles

- **Business-driven design**: All features are directly interpretable in a credit risk context (affordability, employment stability, external creditworthiness, and credit bureau exposure).
- **Missingness as signal**: Missing values are not blindly imputed when they reflect meaningful absence (e.g. no credit history or no external score).
- **Distribution-aware transformations**: Strongly skewed numerical variables are log-transformed to improve model stability.
- **Train–validation consistency**: The same feature definitions and preprocessing logic are applied across all data splits to avoid leakage.

---

### Numerical Features

#### Affordability & Loan Characteristics
- `amt_income_total_log` – log-transformed total income  
- `amt_credit_log` – log-transformed credit amount  
- `amt_annuity_log` – log-transformed annuity  
- `debt_to_income` – annuity-to-income ratio  

Monetary variables exhibit strong right-skewed distributions, which is common in credit risk data. Log transformations reduce the impact of extreme values while preserving relative differences.

#### Employment Stability
- `is_currently_employed` – employment indicator derived from placeholder values  
- `years_employed` – cleaned employment duration in years  

Employment-related placeholder values (e.g. `365243`) are treated as informative signals rather than simple missing values.

#### External Credit Scores
- `ext_source_1`  
- `ext_source_2`  
- `ext_source_3`  

External scores are kept on their original scale to preserve interpretability. Their missingness is explicitly monitored as a risk-related signal.

#### Credit Bureau Aggregates
- `bureau_sum_debt_log` – log-transformed total historical debt  
- `bureau_active_cnt` – number of active bureau credits  
- `bureau_sum_overdue` – total overdue amount  

These features summarize historical credit exposure and repayment pressure.

---

### Categorical Features

The following categorical variables are included and later encoded using one-hot encoding:

- `name_contract_type`  
- `name_income_type`  
- `name_education_type`  
- `name_family_status`  
- `name_housing_type`  

---

### Statistical Validation 

- Pairwise correlations are reviewed across numerical features.
- Expected correlations (e.g. credit–annuity) are observed.
- No severe multicollinearity is detected across major feature groups.

- Chi-square tests are applied to assess the association between categorical features and the target.
- Effect size is evaluated using **Cramér’s V** to control for large-sample significance.
- Results confirm that several categorical variables carry **statistically meaningful but moderate signal**, justifying their inclusion in modeling.

---

### Modeling-Time Missing Value Handling

- **Numerical features**: median imputation  
- **Categorical features**: most frequent category  
- **Informative missingness**: preserved upstream when relevant (e.g. external score availability)

---

### Final Feature Set
- **Grain**: one row per loan application
- **Features**:
  - Transformed numerical features
  - Selected categorical features
- **Target**: default indicator (`target`)

The final feature matrix is saved in Parquet format and serves as direct input for model training.

---

## Modeling

Two models were trained to balance interpretability and predictive performance: a linear baseline model and a non-linear tree-based model.

---

### Baseline Model – Logistic Regression

#### Model Rationale

Logistic Regression was selected as a transparent and interpretable baseline model, which is well aligned with credit risk business requirements and serves as a strong reference point for more complex models.

Class imbalance (~8% default rate) is handled using `class_weight="balanced"`.

#### Preprocessing Pipeline

- **Numerical features**: median imputation + standardization  
- **Categorical features**: most frequent imputation + one-hot encoding  

All preprocessing steps are implemented using a unified `Pipeline` and `ColumnTransformer`.

#### Validation Performance

- **ROC-AUC**: ~0.73  
- **PR-AUC**: ~0.22  

Given the strong class imbalance, PR-AUC is emphasized as a more relevant metric for identifying high-risk applicants.

#### Threshold Optimization

A default threshold of 0.5 is not optimal in this setting. Threshold selection is based on the Precision–Recall curve with a target recall of at least 70%.

- **Selected threshold**: ~0.48  
- **Recall (default class)**: ~70%  

This prioritizes capturing high-risk applicants at the cost of lower precision, which is acceptable in a credit screening context.

---

### Tree-Based Model – HistGradientBoostingClassifier

#### Model Motivation

To capture non-linear relationships and interactions between risk factors, a tree-based model was introduced as a second modeling approach.

Compared to logistic regression, gradient boosting can automatically learn:
- Non-linear effects
- Interaction patterns between affordability, employment, and credit history

HistGradientBoostingClassifier was chosen for its scalability and efficiency on large datasets.

#### Preprocessing Adjustments

- **Numerical features**: median imputation (no scaling, as tree models are scale-invariant)  
- **Categorical features**: most frequent imputation + one-hot encoding  

The feature set remains identical to the baseline model to ensure fair comparison.

#### Model Configuration

- `max_depth = 6`  
- `learning_rate = 0.05`  
- `max_iter = 400`  
- `random_state = 42`  

This configuration balances model expressiveness and generalization.

#### Validation Performance

| Model | ROC-AUC | PR-AUC |
|-----|--------|--------|
| Logistic Regression | ~0.73 | ~0.22 |
| HistGradientBoosting | **~0.75** | **~0.24** |

The tree-based model improves both ranking performance and risk concentration among high-risk applicants.

#### Threshold Optimization

Using the same recall-driven strategy:

- **Target recall**: ≥ 70%  
- **Selected threshold (HGB)**: ~0.076  
- **Recall achieved**: ~70%  

At this operating point, the model captures a large share of default cases while maintaining acceptable precision for a risk screening use case.

---

### Model Comparison Summary

- **Logistic Regression**
  - High interpretability
  - Strong baseline aligned with business transparency requirements
- **HistGradientBoosting**
  - Better non-linear modeling capacity
  - Improved ROC-AUC and PR-AUC
  - Suitable as a production-oriented candidate model

The project adopts a **dual-model strategy**, combining interpretability and predictive power, which reflects real-world credit risk modeling practices.