# claimguard
Insurance Claims Fraud Prioritization System — Data Analytics Capstone

# 🛡️ ClaimGuard — Insurance Claims Fraud Prioritization System

A Data Analytics Capstone Project | Category C: Risk, Fraud, Quality and Compliance

## Problem

Insurance claims are reviewed in the order they arrive, regardless of risk level. This means fraud is often caught late, and investigators waste time on claims that were never risky.

## Solution

ClaimGuard scores every claim for fraud risk the moment it's filed, automatically prioritizing the queue so investigators always know where to look first.

## Live Demo

🔗 https://claimguard-fraud-detection.streamlit.app/

## Dataset

- **Source:** Vehicle Insurance Claim Fraud Detection (Kaggle)
- **Size:** 15,420 claims, 33 columns
- **Grain:** One row = one insurance claim
- **Target:** FraudFound_P (0 = genuine, 1 = fraud)

## Architecture

Business Problem → Data → Quality Checks → SQL/Python → ML/Analytics → Power BI/App → Automated Action → Deployment



## Tech Stack

- **Data & Database:** Python, Pandas, PostgreSQL, Supabase
- **Machine Learning:** scikit-learn (Logistic Regression)
- **Dashboard:** Streamlit, Plotly
- **Business Intelligence:** Power BI
- **Automation:** n8n (daily email alerts)

## Model Performance

| Metric | Score |
|--------|-------|
| Recall (catches real fraud) | 90% |
| Precision (accuracy of alerts) | 13% |

*The model prioritizes catching fraud over avoiding false alarms — appropriate for a first-pass triage tool where a human investigator reviews every flagged claim.*

## Repository Structure


## Tech Stack

- **Data & Database:** Python, Pandas, PostgreSQL, Supabase
- **Machine Learning:** scikit-learn (Logistic Regression)
- **Dashboard:** Streamlit, Plotly
- **Business Intelligence:** Power BI
- **Automation:** n8n (daily email alerts)

## Model Performance

claimguard/
├── app.py                # Streamlit dashboard
├── requirements.txt      # Python dependencies
├── claimguard_model.pkl  # Trained model
├── model_columns.pkl     # Model feature columns
├── data/                 # Dataset
├── notebooks/            # EDA and model training
├── sql/                  # Database schema
├── visuals/              # EDA charts
└── powerbi/              # Power BI report





## How to Run Locally

```bash
git clone https://github.com/Prachi217/claimguard.git
cd claimguard
pip install -r requirements.txt
streamlit run app.py
```

## Key Findings from EDA

- Fraud rate is ~9x higher when the policyholder (not a third party) was at fault
- Claims with no police report or no witness show significantly higher fraud rates
- Utility vehicles have the highest fraud rate among categories

## Limitations

- Built on a public dataset — may not fully reflect a real insurer's internal data patterns
- PolicyNumber and RepNumber were excluded as identifiers, not predictive features
- Precision is low by design — this tool supports human review, it does not replace it

## Author

Prachi Vishwakarma — Data Analytics Capstone Project, SURE TRUST PROED
