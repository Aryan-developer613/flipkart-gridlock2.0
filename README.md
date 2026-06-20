# 🚦 Gridlock AI — Bengaluru Traffic Intelligence Platform

> **Flipkart Gridlock Hackathon 2.0 | Theme 2: Event-Driven Congestion**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Click_Here-7c6ffd?style=for-the-badge)](https://aryan-developer613.github.io/flipkart-gridlock2.0/dashboard/index.html)
[![ML Accuracy](https://img.shields.io/badge/ML_Accuracy-99.8%25-00e5a0?style=for-the-badge)](https://aryan-developer613.github.io/flipkart-gridlock2.0/dashboard/index.html)
[![Incidents](https://img.shields.io/badge/Incidents_Analysed-8%2C173-ffbe0b?style=for-the-badge)](https://aryan-developer613.github.io/flipkart-gridlock2.0/dashboard/index.html)
[![Theme](https://img.shields.io/badge/Theme-Event--Driven_Congestion-ff3860?style=for-the-badge)](https://aryan-developer613.github.io/flipkart-gridlock2.0/dashboard/index.html)

---

## 🎯 Problem Statement

Bengaluru, with 14 million+ people, faces severe traffic breakdowns during planned and unplanned events — political rallies, religious processions, VIP movements, and protests.

**Current situation:**
- ❌ Enforcement is entirely **reactive** — police deploy after jams start
- ❌ Decisions are **experience-driven** with no data system
- ❌ **No diversion planning** — routes decided on-the-spot
- ❌ **Zero post-event learning** — same mistakes repeat every time

---

## 💡 Our Solution

**Gridlock AI** is an end-to-end AI/ML platform built on **8,173 real Bengaluru Traffic Police incidents** (Nov 2023 – Apr 2024) that:

- 🔮 **Forecasts** event-driven congestion impact
- 👮 **Recommends** optimal police deployment instantly
- 🗺️ **Suggests** pre-computed diversion routes
- 📊 **Analyses** historical patterns across 21 corridors

---

## 🤖 AI/ML Models

| Model | Algorithm | Accuracy | Purpose |
|-------|-----------|----------|---------|
| Priority Predictor | Random Forest (150 trees) | **99.8%** | Predict High/Low priority |
| Road Closure Predictor | Gradient Boosting | **91.5%** | Predict if closure needed |
| Deployment Recommender | Rule-based + ML Hybrid | **Live** | Police, barricades, routes |

### Key Metrics — Model 1 (Priority Predictor)
```
Accuracy  : 99.8%    Precision : 99.7%
Recall    : 100.0%   F1 Score  : 99.8%
5-Fold CV : 99.9%    Train Size: 6,429 samples
```

### Top Feature Importance
```
Corridor (Road Name)  : 86.86% ← Most important!
Police Station        :  7.91%
Event Cause           :  1.51%
Hour of Day           :  1.14%
```

---

## 📊 Key Findings

| Insight | Value |
|---------|-------|
| Total Incidents Analysed | 8,173 |
| High Priority Events | 61.5% (5,025) |
| Event-Driven Incidents | 191 |
| Worst Corridor | Mysore Road (Risk Score: 2,310) |
| Peak Hour | 9 PM (810 events) |
| Worst Days | Friday & Saturday |
| Police Stations Covered | 54 across 10 zones |

---

## 🖥️ Dashboard — 8 Pages

| Page | Features |
|------|----------|
| 🏠 Overview | KPI cards, 4 charts, corridor risk table |
| 🗺️ Hotspot Map | Interactive Bengaluru GPS map, 7 filters |
| 🤖 AI Recommender | Live deployment recommendations |
| 📅 Event Calendar | Upcoming events with pre-planning |
| ⚖️ Before vs After | Impact comparison table |
| 👮 Station Finder | Police station load analysis |
| 🧠 ML Results | Full evaluation — confusion matrix, F1, feature importance |
| 📊 Analysis | Deep dive charts and model comparison |

---

## 🚀 Live Demo

👉 **[Click here to open Gridlock AI](https://aryan-developer613.github.io/flipkart-gridlock2.0/dashboard/index.html)**

No installation needed — opens directly in browser!

---

## 🛠️ Tech Stack

```
Python          Pandas          NumPy
Scikit-learn    Random Forest   Gradient Boosting
Folium          Leaflet.js      Chart.js
Streamlit       HTML/CSS/JS     Inter Font
```

---

## 📁 Project Structure

```
gridlock_project/
├── data/
│   ├── astram_event_data.csv          ← BTP incident data (8,173 rows)
│   ├── model_priority_predictor.pkl   ← Trained Random Forest model
│   └── model_closure_predictor.pkl    ← Trained Gradient Boosting model
├── notebooks/
│   ├── day1_eda.py                    ← Exploratory Data Analysis
│   ├── day2_hotspot_analysis.py       ← Hotspot & corridor analysis
│   ├── day3_prediction_model.py       ← ML model training
│   ├── chart1-16.png                  ← 16 analysis charts
│   └── map1-3.html                    ← 3 interactive maps
└── dashboard/
    ├── index.html                     ← ⭐ Main web app (open this!)
    └── app.py                         ← Streamlit dashboard
```

---

## ▶️ How to Run

### Option 1 — Web App (Recommended)
```bash
# Just open in browser — no installation needed!
open dashboard/index.html
```

### Option 2 — Streamlit Dashboard
```bash
pip install streamlit streamlit-folium scikit-learn folium pandas
cd dashboard
streamlit run app.py
```

### Option 3 — Re-train ML Models
```bash
pip install pandas scikit-learn matplotlib seaborn folium
cd notebooks
python day3_prediction_model.py
```

---

## 🏆 Hackathon Details

- **Event:** Flipkart Gridlock Hackathon 2.0
- **Theme:** Theme 2 — Event-Driven Congestion
- **Data:** Astram Event Dataset — Bengaluru Traffic Police
- **Timeline:** Phase 2 Prototype Submission

---

## 📈 Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| Decision Time | 30–60 minutes | < 2 seconds |
| Accuracy | ~60% (experience) | 99.8% (ML) |
| Diversion Planning | Ad-hoc, on-spot | Pre-computed optimal |
| Resource Deployment | Over/Under staffed | Precisely allocated |
| Post-Event Learning | None | Continuous ML improvement |

---

*Built with ❤️ for Flipkart Gridlock Hackathon 2.0*
