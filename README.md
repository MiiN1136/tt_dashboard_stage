# TT Healthcare Intelligence
> 📄 **Version Française :** Le rapport de projet complet en français est disponible au format PDF [ici](https://github.com/MiiN1136/tt_dashboard_stage/releases/download/v1.0.0/ttStage.pdf).

An end-to-end **BI + AI healthcare analytics platform** built for **Tunisie Telecom (TT)**.  
The project combines **real HR data** from TT with a **synthetic myCover-like healthcare dataset** to simulate employee healthcare usage, visualize cost drivers, and predict healthcare costs at the employee level.

The solution includes:

- a **FastAPI backend** serving predictions and analytics endpoints,
- a **Streamlit frontend** for interactive BI dashboards,
- a **machine learning model** to predict healthcare costs per employee,
- and a **deployment on Render** for both backend and frontend.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Business Context](#business-context)
- [Data Sources](#data-sources)
- [Synthetic Data Generation Strategy](#synthetic-data-generation-strategy)
- [Feature Engineering and Preprocessing](#feature-engineering-and-preprocessing)
- [Machine Learning Approach](#machine-learning-approach)
- [System Architecture](#system-architecture)
- [Backend (FastAPI)](#backend-fastapi)
- [Frontend (Streamlit)](#frontend-streamlit)
- [API Endpoints](#api-endpoints)
- [How to Run Locally](#how-to-run-locally)
- [Deployment on Render](#deployment-on-render)
- [Repository Structure](#repository-structure)
- [Key Insights and Dashboard Views](#key-insights-and-dashboard-views)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Acknowledgements](#acknowledgements)

---

## Project Overview

This project was developed as a decision-support system for **TT stakeholders**.  
Its main goal is to help management understand healthcare spending patterns, identify cost drivers, and support strategic decisions related to employee healthcare benefits.

The platform answers questions such as:

- Which employee profiles generate the highest healthcare cost?
- Which diseases or service types are the biggest cost drivers?
- How do healthcare expenses evolve over time?
- Which cohorts appear more expensive from a healthcare perspective?
- What is the predicted healthcare cost of a given employee profile?

The final product is a **modern BI dashboard** enhanced with **machine learning**.

---

## Business Context

The project is centered around **Tunisie Telecom – Direction Régionale de Nabeul** and the broader TT employee population.

The original challenge was that healthcare records are confidential and cannot be accessed freely.  
To overcome this, the project uses:

1. **Real HR data** collected from TT in 2019,
2. **Synthetic myCover-style healthcare records** generated from real employee profiles,
3. A **prediction model** trained on the generated healthcare behavior,
4. An **interactive dashboard** for business users.

This makes the system useful for:

- HR and employee wellbeing analysis,
- budget estimation,
- yearly cost anticipation,
- healthcare benefit evaluation,
- and contract/benefit strategy discussions.

---

## Data Sources

### 1) Real HR Dataset
The HR data was extracted from a multi-sheet Excel file containing TT personnel records by region and department.

It includes fields such as:

- employee name,
- matricule,
- grade,
- category,
- corps,
- date of birth,
- entry date,
- retirement date,
- assignment,
- region.

The HR dataset was originally a **2019 snapshot** and had to be cleaned heavily because:
- the workbook had multiple sheets,
- each sheet contained metadata lines before the header row,
- some columns were unnamed,
- the content mixed French and Arabic names.

### 2) Synthetic myCover Dataset
Since actual myCover records are confidential, the healthcare dataset was **generated synthetically** using:
- the real TT HR population,
- realistic household logic,
- age-based chronic disease probabilities,
- service-type probability distributions,
- realistic cost ranges inspired by observed examples from myCover.

### 3) One Real myCover Example
The project also used a **single real myCover record example** to understand the structure of:
- bulletin number,
- patient,
- date sinistre,
- date remboursement,
- prestataire,
- type de prestation,
- total dépensé,
- total remboursé.

This example helped anchor the synthetic generation logic so that the simulated dataset resembles the real application format.

---

## Synthetic Data Generation Strategy

The healthcare dataset was not generated randomly from scratch.  
It was created using a **hybrid strategy**:

- **real TT employee profiles** as the base population,
- **synthetic household structure** around adherents,
- **synthetic healthcare events** following realistic rules.

### Main rules used

- one employee = one adherent profile,
- spouse age remains consistent per household,
- each person in the household can have their own chronic condition,
- chronic disease is not automatically inherited across the family,
- events are constrained by retirement date,
- events are generated within a realistic time window,
- event types follow age-dependent probabilities,
- maternity-like clinic events are only simulated for plausible household cases,
- reimbursement delay is generated only when the claim is marked as reimbursed.

### Healthcare event types
The synthetic myCover data includes the same main categories observed in the real system:

- Pharmacie
- Laboratoire
- Consultation
- Radio
- Clinique

### Cost logic
The cost ranges were tuned to resemble observed values from the example data, including:
- low-cost pharmacy claims,
- moderate laboratory and consultation claims,
- high-cost clinic claims,
- reimbursement amounts consistent with the type of service.

---

## Feature Engineering and Preprocessing

To prepare the dataset for AI, the project created a dedicated ML dataframe.

### Raw / BI-friendly dataset
This version keeps readable, business-friendly values:
- service names,
- disease labels,
- dates,
- amounts,
- relationship names.

It is used mainly for:
- BI dashboards,
- KPI display,
- trend analysis,
- stakeholder-facing reports.

### ML-ready dataset
This version is transformed for model training and prediction:
- `Chronic_Disease` → one-hot encoded,
- `Relationship` → one-hot encoded,
- `Type_Prestation` → one-hot encoded,
- `Etat` → label encoded,
- `Date_Remboursement` → converted into delay/time features,
- `Dependent_Age` → binned,
- identifiers are removed from the model input.

### Examples of engineered features
- `Delay_Remboursement`
- `Dependent_Age` bins
- `Chronic_Disease_*`
- `Relationship_*`
- `Type_Prestation_*`

The result is a consistent ML dataset with **2453 rows and 20 columns** before the final model selection stage.

---

## Machine Learning Approach

The project’s ML objective is to predict **healthcare cost per employee** in a way that is useful for TT stakeholders.

### Main model
A regression model was trained to estimate healthcare cost based on employee and healthcare-event features.

### Why this model matters
The model helps TT management:
- estimate expected healthcare spending,
- identify expensive employee profiles,
- evaluate cost concentration by disease or service type,
- support yearly budget and benefit planning.

### Important note
Because the synthetic healthcare data was generated using business rules, the model is primarily a **decision-support and pattern analysis tool**, not a clinical model.

---

## System Architecture

The system follows a clean multi-layer architecture:

### 1) Data layer
- real HR data,
- synthetic healthcare dataset.

### 2) Modeling layer
- preprocessing,
- feature engineering,
- ML training,
- prediction export.

### 3) API layer
- FastAPI backend,
- model inference,
- business analytics endpoints.

### 4) Presentation layer
- Streamlit dashboard,
- charts,
- KPI cards,
- employee lookup page,
- simulation page.

### 5) Deployment layer
- backend deployed on Render,
- frontend deployed on Render.

---

## Backend (FastAPI)

The backend is implemented with **FastAPI** and serves as the central data and prediction engine.

### Main responsibilities
- load the trained model,
- load preprocessed datasets,
- expose prediction endpoints,
- compute risk scores,
- deliver KPI data,
- aggregate disease and time-based analytics,
- support employee-level lookup,
- enable what-if scenarios.

### Key backend behaviors
- automatic feature alignment before prediction,
- fallback handling for missing columns,
- cost-to-risk mapping,
- aggregation by disease, cohort, and month,
- employee profile retrieval.

### Backend technologies
- FastAPI
- pandas
- NumPy
- joblib
- scikit-learn
- CORS middleware

---

## Frontend (Streamlit)

The frontend is built using **Streamlit** and provides a polished BI interface for stakeholders.

### Pages
#### 1) Enterprise Overview
A high-level executive view with:
- total predicted cost,
- average predicted cost,
- high-risk employee count,
- total employees,
- risk distribution pie chart,
- disease burden chart,
- cohort cost curve,
- feature sensitivity visualization.

#### 2) Advanced Analytics
A deeper analytics page with:
- age-stratified risk heatmap,
- 3-factor cost cube,
- high-risk registry,
- cross-segment visual exploration.

#### 3) Employee Registry
An employee search and profile page with:
- matricule lookup,
- employee age,
- predicted cost,
- service usage summary,
- claim history,
- cost evolution,
- risk evolution,
- clinic/service utilization trend.

#### 4) Neural Simulation
A what-if simulator that allows scenario-based cost estimation.

### Frontend design style
The dashboard uses:
- a clean light theme,
- custom cards,
- custom SVG icons,
- modern spacing,
- responsive layout,
- Plotly charts for interactivity.

---

## API Endpoints

The backend exposes several endpoints used by the frontend.

### `POST /predict`
Predict healthcare cost for a given employee feature vector.

Returns:
- predicted cost,
- risk score,
- risk level.

### `GET /high-risk`
Returns the list of employees predicted as high risk.

### `GET /risk-distribution`
Returns the distribution of risk levels.

### `GET /cost-by-disease`
Returns total cost grouped by disease category.

### `GET /risk-heatmap-age`
Returns an age-by-risk heatmap table.

### `GET /kpis`
Returns top-level dashboard KPIs.

### `GET /cost-drivers`
Returns the most important cost drivers.

### `GET /employee/{matricule}`
Returns an employee profile, claim history, and predicted cost.

### `GET /cohorts`
Returns average predicted cost by age cohort.

### `POST /what-if`
Simulates a scenario and compares baseline cost vs scenario cost.

### `GET /risk-matrix`
Returns a multi-dimensional risk matrix.

### `GET /cost-trend`
Returns monthly total cost trend.

### `GET /risk-trend`
Returns monthly risk evolution.

### `GET /clinic-trend`
Returns monthly utilization trend by service type.

### `GET /avg-cost-trend`
Returns monthly average cost trend.

---

## How to Run Locally

### 1) Clone the repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2) Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# or
.venv\Scripts\activate      # Windows
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Run the backend
```bash
uvicorn main:app --reload
```

### 5) Run the frontend
```bash
streamlit run app.py
```

### 6) Open the dashboard
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:8501`

---

## Deployment on Render

The project is deployed on **Render** in two separate services:

### Backend
- FastAPI service hosted on Render
- provides the model inference API and analytics endpoints

### Frontend
- Streamlit service hosted on Render
- consumes the backend API and renders the BI dashboard

This deployment setup makes the project accessible online without requiring local installation.

---

## Repository Structure

A typical structure may look like this:

```text
.
├── backend/
│   ├── main.py
│   ├── model.pkl
│   ├── features.pkl
│   ├── employee_risk.csv
│   ├── df_cleaned.csv
│   └── full_hr.csv
├── frontend/
│   └── app.py
├── data/
│   ├── full_hr.csv
│   ├── df_cleaned.csv
│   └── employee_risk.csv
├── notebooks/
│   └── data_preparation.ipynb
├── requirements.txt
└── README.md
```

---

## Key Insights and Dashboard Views

The dashboard was designed to answer concrete business questions.

### Examples of useful insights
- Which chronic diseases generate the highest cost?
- Which age cohorts have the highest projected cost?
- Which service type is most expensive?
- Which employees should be monitored as high-cost cases?
- How does healthcare spending evolve over time?
- Which cohorts look more “burdensome” from a healthcare perspective?

### Why this matters for TT
For TT stakeholders, the project can help with:
- annual expense planning,
- benefit strategy evaluation,
- understanding the value of the healthcare agreement,
- assessing employee wellbeing trends,
- supporting management decisions with visual evidence.

---

## Limitations

This project was designed under real-world constraints:

- the full myCover dataset was confidential and inaccessible,
- only one real myCover example record was available,
- some employee attributes such as gender or marital status were not available,
- the healthcare dataset had to be simulated from real HR structure,
- the model is a decision-support model, not a medical diagnosis tool.

These limitations were handled by building a strong synthetic but realistic dataset and by keeping the business interpretation focused on TT management use cases.

---

## Future Improvements

Possible future enhancements include:

- richer household simulation,
- more granular service types,
- additional employee-level aggregation models,
- stronger time-series forecasting,
- role-based dashboards for HR, finance, and management,
- more detailed scenario analysis,
- improved explainability with SHAP or permutation importance.

---

## Acknowledgements

This project was built around the TT environment and the healthcare workflow observed in myCover.

Special thanks to the TT supervision context for allowing the project to be shaped around a real business problem, a real HR base, and a realistic operational dashboard.

---

## Note

The project uses **real HR information** and **synthetic healthcare events** to preserve confidentiality while still delivering a meaningful and realistic analytics system.
