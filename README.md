# Home Credit Risk Analytics

<p align="center">
  <img src="images/home_credit_logo.png" width="320">
</p>

## Project Overview

This project focuses on **credit risk analysis and default prediction** in a consumer lending context.

Inaccurate risk assessment can lead to financial losses:
- Underestimating risk increases defaults  
- Overestimating risk rejects good customers and limits growth  

The goal of this project is to build an **end-to-end analytics pipeline** that turns raw credit data into **actionable risk insights and decision support**, including:
- Risk analysis using SQL  
- Interactive dashboards  
- Predictive modeling  
- A deployable API and demo application  

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

## Data & Key Challenges

The dataset represents real-world credit data with:
- Multiple relational tables (applications, bureau records, repayment history)
- One customer appearing across many records
- Strong class imbalance (default rate around 8%)

Key challenges include:
- High missingness across many features  
- Mixed business-driven and technical missing values  
- Strongly skewed financial variables  
- The need to aggregate raw data into applicant-level features  

---

## Data Cleaning Strategy

A **risk-aware and careful cleaning strategy** was applied:

- Missing values were **kept and flagged** where possible, as missingness itself can be a risk signal  
- Known technical placeholders were converted to null values  
- Extreme values were **clipped instead of dropping rows** to reduce outlier impact while preserving sample size  
- Identical rules were applied to training and validation data to ensure consistency  

---

## Key Business Questions

This analysis is guided by four business-driven questions:

1. Who is more likely to default?  
2. Does previous loan refusal signal higher future risk?  
3. How does repayment behavior affect default risk?  
4. Do multiple risk signals reinforce each other?  

---

## Risk Analysis & Insights

### Customer Profile Risk
Higher default risk concentrates among:
- Lower education levels  
- Lower income groups  
- Single applicants  

However, demographic features alone provide limited risk separation.

---

### Credit Bureau Risk
- Default risk increases as debt levels rise  
- Applicants with **no bureau records** show risk levels similar to highly indebted customers  
- Bureau data enables strong risk segmentation  

---

### Repayment Behavior
- Frequent late payments are the strongest behavioral risk signal  
- Default risk rises sharply with repayment delinquency  

---

### Combined Risk Effects
Default risk increases significantly when **high debt burden and poor repayment behavior occur together**,  
showing that **combined signals make risk easier to understand than single features on their own**.

---

## Feature Engineering & Modeling

Features were grouped into three main categories:
- Demographic features  
- Credit bureau features  
- Behavioral and repayment features  

Two models were built and compared:
- **Logistic Regression** as a simple baseline model  
- **Gradient Boosting** as a more flexible, non-linear model  

Due to strong class imbalance, model performance was evaluated using **ranking-based metrics**:
- ROC–AUC to assess overall ranking quality  
- PR–AUC to better reflect performance in identifying defaulters  

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

---

## Credit Risk Scoring API & Demo

This project deploys a credit risk model as a production-style API with a lightweight Streamlit demo for business users.

---

### FastAPI Service

Start the API:

```bash
uv run uvicorn api.main:app --reload
```

- Docs: http://127.0.0.1:8000/docs
- Endpoint: POST /predict

### Streamlit Demo

Run the demo UI (in a separate terminal):

```bash
uv run streamlit run dashboard/app.py
```

This demonstrates how analytics can move beyond analysis into **practical decision support**.

---

## Credit Risk Dashboard

A Tableau dashboard was created to visualize portfolio-level credit risk and customer risk profiles.  
It includes key KPIs, default rate segmentation by customer characteristics, and a drill-down filter by employment status.

🔗 **Tableau Public Dashboard:**  
https://public.tableau.com/app/profile/ou.hai/viz/HomeCredit_CreditRiskDashboard

---

## Key Takeaways

- Behavioral and bureau signals dominate static demographics  
- Missing data often reflects uncertainty-driven risk  
- Non-linear models improve risk ranking under class imbalance  
- Decision thresholds must align with business risk appetite  

---

## Challenges

This project involves several important challenges:

- Credit data is **high-dimensional and highly relational**, requiring careful aggregation and feature design  
- Risk signals come from **multiple dimensions**, which makes them harder to explain clearly  
- Strong class imbalance requires **business-driven evaluation and threshold selection**, rather than default model settings  

---

## Next Steps

Future improvements could further enhance risk identification and decision quality:

- Add **time-based repayment behavior** to capture early warning signals  
- Use **more detailed behavioral features** to improve risk differentiation  
- Further **tune decision thresholds based on business needs** and risk appetite

---

## Presentation

- 📊 **Project Presentation Slides**:  
  https://www.canva.com/design/DAG_mkUmP2Q/rdIciHDiB1ti1N1dh8ayRw/edit?utm_content=DAG_mkUmP2Q&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton