"""
Script to generate the revised undergraduate engineering mini-project report
for N²M Flood Prediction Model in Markdown format (`reports/final_report/report.md`).
Written in clear, straightforward, student-appropriate engineering language.
"""

import os

REPORT_MD_PATH = "reports/final_report/report.md"

FRONT_MATTER = """# N²M FLOOD PREDICTION MODEL
## An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru

---

### Academic Project Report
**Submitted in partial fulfillment of the requirements for the Degree of**  
**Bachelor of Engineering in Computer Science and Engineering**

**Department of Computer Science & Engineering**  
**Dayananda Sagar College of Engineering**  
*(An Autonomous Institute Affiliated to VTU, Belagavi, Approved by AICTE & UGC)*  
**Shavige Malleshwara Hills, Kumaraswamy Layout, Bengaluru – 560078**  
**Academic Year: 2026 – 2027**

---

### Project Group Members
- **Nishanth G M** (USN: 1DS23CS...) — *Data Pipeline, Hydrological Features & GIS Extraction*
- **Mohith M** (USN: 1DS23CS...) — *Machine Learning Model, Class Imbalance Tuning & Validation*
- **Nihal Rao** (USN: 1DS23CS...) — *Full-Stack Architecture, Map Visualization & Demonstration Bot*

**Under the Guidance of:**  
**Dr. Punith Kumar**  
Associate Professor, Department of Computer Science & Engineering  
Dayananda Sagar College of Engineering, Bengaluru

---

## ABSTRACT

Urban flooding has become a frequent and disruptive problem in Bengaluru during the monsoon season. Rapid urban construction over the past few decades has covered large areas of natural soil with asphalt and concrete. This widespread concrete cover prevents rainwater from soaking into the ground, while also putting severe pressure on historical stormwater drains (*rajakaluves*) and interconnected lake chains (*keres*). When heavy rains occur, low-lying valleys, underpasses, and road intersections often experience waterlogging. Traditional municipal flood advisories are typically issued at the whole-city or taluk level, which does not provide residents or engineers with local, neighborhood-level insight into which specific areas are physically most prone to water accumulation.

In this mini-project, our student team designed and developed the **N²M Flood Prediction Model**, an experimental data science and web visualization system that maps relative flood susceptibility across Greater Bengaluru. We divided the 711.59 km² municipal area into a uniform Cartesian grid of **3,026 spatial cells**, each measuring approximately 500 m × 500 m (0.25 km²). For each cell, we calculated 10 static terrain and built-environment features (such as elevation, slope, Topographic Wetness Index, Height Above Nearest Drainage, impervious surface fraction, and distances to lakes, drains, and roads) using open datasets from SRTM DEM, ESA WorldCover, and OpenStreetMap. In addition, we linked each cell to daily rainfall estimates from the CHIRPS satellite-gauge dataset, creating 8 dynamic rainfall features including multi-day rolling sums and antecedent lag values.

To model flood susceptibility, we trained an **XGBoost** machine learning classifier. Because confirmed historical flood records are extremely rare—accounting for only 240 positive cell-days across roughly 1.76 million historical records—we configured the model with positive class weighting (`scale_pos_weight = 89.16`) and adopted a daily rank-based evaluation approach. Instead of relying on rigid probability cutoffs, the model ranks all 3,026 cells from highest to lowest susceptibility for any given day, grouping them into High Priority (Top 150 cells / ~5%), Moderate Priority (Ranks 151–300 / ~5%), and Baseline Risk (Ranks 301–3,026 / ~90%). 

We evaluated our model on the major September 2022 monsoon flood sequence, which was held out completely during training. The model achieved a Precision-Recall Area Under Curve (PR-AUC) of **0.0026**, which is **2.0× higher than random guessing (0.0013)**. More importantly for practical inspection, the top 10% ranked cells captured **25.0% of all confirmed historical flood locations**, representing a **2.53× enrichment factor**. We deployed the system with a Python FastAPI backend hosted on Render and an interactive React web dashboard on Vercel. The web map renders all 3,026 cells smoothly at 60 frames per second using an HTML5 Canvas layer on Leaflet, and includes an interactive 24-day historical replay and a private demonstration Telegram bot. All 82 automated backend test cases pass successfully. This project demonstrates how open geospatial datasets and machine learning can be combined to build an accessible, educational tool for studying urban flood susceptibility.

**Keywords**: Urban Flood Susceptibility, Machine Learning, XGBoost, Bengaluru Drainage, Geospatial Data Science, Topographic Wetness Index, FastAPI, React, Leaflet Canvas.

---

## TABLE OF CONTENTS

- **Front Matter**
  - Title & Academic Submission Details
  - Abstract
  - Table of Contents
  - List of Figures
  - List of Tables
  - List of Abbreviations
- **Chapter 1: Introduction**
  - 1.1 Background of Urban Flooding
  - 1.2 Urban Flooding Challenges in Bengaluru
  - 1.3 Why Machine Learning Helps in Flood Susceptibility Studies
  - 1.4 Motivation for the Project
  - 1.5 Project Objectives
  - 1.6 Scope and Practical Limitations
  - 1.7 Organization of the Report
- **Chapter 2: Literature Review**
  - 2.1 Urban Flood Susceptibility Mapping Approaches
  - 2.2 Machine Learning in Flood-Related Studies
  - 2.3 Rainfall and Hydrological Studies in Bengaluru
  - 2.4 Technology-Enabled Flood Information Platforms
  - 2.5 Comparative Analysis of Reviewed Literature (Table 1)
  - 2.6 Project Motivation and Identified Gaps
- **Chapter 3: Problem Statement and Proposed Solution**
  - 3.1 Problem Statement
  - 3.2 Existing Challenges
  - 3.3 Proposed Solution
  - 3.4 Functional Requirements (Table 2)
  - 3.5 Non-Functional Requirements (Table 3)
  - 3.6 Scope and Operational Boundaries
- **Chapter 4: System Design and Architecture**
  - 4.1 Overall System Architecture (Figure 1)
  - 4.2 Geospatial Data Processing Pipeline (Figure 2)
  - 4.3 Machine Learning Component
  - 4.4 Backend Architecture and REST API (Table 4)
  - 4.5 Frontend Web Application and Map Architecture
  - 4.6 Historical Replay Mechanism
  - 4.7 Telegram Demonstration Bot Integration
  - 4.8 Cloud Deployment Architecture
- **Chapter 5: Methodology**
  - 5.1 Dataset and Data Sources (Table 5)
  - 5.2 Spatial Grid Discretization (3,026 Cells)
  - 5.3 Input Features and Descriptions (Table 6)
  - 5.4 Data Preprocessing and Feature Calculation
  - 5.5 Ground-Truth Flood Labels and Extreme Imbalance (Table 7)
  - 5.6 Model Selection and XGBoost Configuration (Table 8)
  - 5.7 Daily Susceptibility Ranking Methodology (Figure 3 & Table 9)
  - 5.8 Out-of-Sample Holdout Evaluation Protocol
- **Chapter 6: Implementation and Results**
  - 6.1 Technologies and Tools Used (Table 11)
  - 6.2 Data Pipeline Implementation
  - 6.3 Machine Learning and Ranking Implementation
  - 6.4 Backend Service Implementation
  - 6.5 Frontend Map Implementation (Figure 4)
  - 6.6 Historical Replay and Rainfall Trends (Figure 5)
  - 6.7 Telegram Demonstration Bot Implementation
  - 6.8 Automated Testing Suite (Table 12)
  - 6.9 Deployment Setup on Vercel and Render
  - 6.10 Experimental Results and Plain Language Explanation (Table 10)
- **Chapter 7: Conclusion and Future Scope**
  - 7.1 Project Summary
  - 7.2 What the Group Successfully Implemented
  - 7.3 Main Engineering Observations
  - 7.4 Practical Limitations
  - 7.5 Future Work and Scope for Improvement
- **References**

---

## LIST OF FIGURES

- **Figure 1**: Overall System Architecture of the N²M Flood Prediction Model
- **Figure 2**: Geospatial Data Ingestion and Feature Processing Pipeline
- **Figure 3**: XGBoost Inference and Daily Spatial Ranking Flowchart
- **Figure 4**: Interactive Cartographic Web Interface Showing Bengaluru Flood Grid
- **Figure 5**: Historical Daily Rainfall Trend Across Bengaluru During September 2022

---

## LIST OF TABLES

- **Table 1**: Comparative Summary of Reviewed Literature
- **Table 2**: Functional Requirements Specification
- **Table 3**: Non-Functional Requirements Specification
- **Table 4**: Complete Backend REST API Directory
- **Table 5**: Primary Datasets and Geospatial Sources
- **Table 6**: Complete Feature Set (18 Parameters)
- **Table 7**: Historical Flood Events and Label Breakdown
- **Table 8**: XGBoost Model Hyperparameter Settings
- **Table 9**: Daily Susceptibility Ranking Tiers
- **Table 10**: Holdout Model Performance Metrics (September 2022 Benchmark)
- **Table 11**: Software Dependencies and Libraries Used
- **Table 12**: Automated Backend Test Suite Results

---

## LIST OF ABBREVIATIONS

- **API**: Application Programming Interface
- **BBMP**: Bruhat Bengaluru Mahanagara Palike
- **CHIRPS**: Climate Hazards Center InfraRed Precipitation with Stations
- **CSV**: Comma-Separated Values
- **DEM**: Digital Elevation Model
- **ESA**: European Space Agency
- **GIS**: Geographic Information System
- **HAND**: Height Above Nearest Drainage
- **HTML5**: HyperText Markup Language version 5
- **IMD**: India Meteorological Department
- **JSON**: JavaScript Object Notation
- **KSNDMC**: Karnataka State Natural Disaster Monitoring Centre
- **ML**: Machine Learning
- **N2M**: Nishanth, Nihal, Mohith (Student Team Initials)
- **OSM**: OpenStreetMap
- **PR-AUC**: Precision-Recall Area Under the Curve
- **RAM**: Random Access Memory
- **REST**: Representational State Transfer
- **ROC-AUC**: Receiver Operating Characteristic Area Under the Curve
- **SRTM**: Shuttle Radar Topography Mission
- **TTL**: Time To Live
- **TWI**: Topographic Wetness Index
- **UI**: User Interface
- **URI / URL**: Uniform Resource Identifier / Locator
- **Vite**: Modern JavaScript Build Tool
- **XGBoost**: eXtreme Gradient Boosting
"""
