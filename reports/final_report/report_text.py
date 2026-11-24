"""
N²M Flood Prediction Model — Full Text Content for Academic Report
===================================================================
Contains comprehensive academic chapters, tables, captions, and references.
"""

FRONT_MATTER_MD = r"""# N²M FLOOD PREDICTION MODEL: AN ML-BASED URBAN FLOOD SUSCEPTIBILITY MAPPING AND VISUALIZATION SYSTEM FOR BENGALURU

**A Technical Project Report Submitted in Partial Fulfillment of the Requirements for the Degree of Bachelor of Engineering in Computer Science and Engineering**

---

### Academic Submission & Project Identity
- **Project Title**: N²M Flood Prediction Model — An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru
- **Institution**: Dayananda Sagar College of Engineering, Bengaluru, Karnataka, India
- **Department**: Department of Computer Science & Engineering
- **Academic Year**: 2026–2027
- **Faculty Project Advisor**: Dr. Punith Kumar, Associate Professor, Department of Computer Science & Engineering
- **Student Contributors**:
  - **Nishanth G M** (Data Ingestion Pipeline, Hydrological Extraction, Terrain Feature Engineering)
  - **Mohith M** (Machine Learning Architecture, Extreme Class Imbalance Tuning, Holdout Validation)
  - **Nihal Rao** (Full-Stack Architecture, GIS Cartographic Engine, Interactive Replay Dashboard)
- **Institutional Address**: Shavige Malleshwara Hills, Kumaraswamy Layout, Bengaluru, Karnataka 560078, India
- **Repository**: `https://github.com/nishanth-end/n2m-rain-model`

---

## ABSTRACT

Urban flooding in rapidly expanding Indian metropolises has evolved from an occasional seasonal hazard into a recurrent, catastrophic infrastructure crisis. In Greater Bengaluru (Bruhat Bengaluru Mahanagara Palike — BBMP), rapid and uncontrolled urban growth over the past four decades has expanded impervious surface cover from less than 8% in 1973 to over 93% in 2020. This transformation has encroached on interconnected lake cascades (*keres*), severed natural primary stormwater channels (*rajakaluves*), and created localized ponding zones across low-lying valleys. Concurrently, tropical convective storms frequently drop 70 to 120 mm of precipitation within 60 to 90 minutes over isolated sectors of the city while adjacent administrative zones remain dry. Conventional municipal flood warnings remain generalized at the municipal or taluk scale, providing zero actionable spatial differentiation for micro-catchments, underpasses, and low-lying valleys.

This project presents the design, implementation, evaluation, and deployment of the **N²M Flood Prediction Model**, an integrated geospatial data science platform that evaluates relative spatial flood susceptibility across Greater Bengaluru (711.59 km²). The system discretizes the urban domain into a uniform Cartesian mesh of **3,026 spatial cells** (~500 m × 500 m, 0.25 km² per cell) spanning all 198 BBMP administrative wards. Each grid cell is parameterized with 18 physical features, combining 10 static terrain morphology indices (elevation, slope, Topographic Wetness Index [TWI], Height Above Nearest Drainage [HAND], contributing catchment area, impervious fraction, lake/drain/road proximities, and waterbody density) derived from SRTM DEM, ESA WorldCover, and OpenStreetMap, with 8 dynamic antecedent precipitation matrices derived from 0.05° gridded CHIRPS satellite-gauge observations.

An extreme gradient-boosted decision tree ensemble (**XGBoost**) is trained to score daily cell susceptibility. To overcome extreme historical flood label sparsity (240 positive cell-days across 1.76 million cell-days, or 0.0136% prevalence), the model incorporates heavy positive weighting (`scale_pos_weight = 89.16`) and replaces uncalibrated absolute probability thresholds with an operational **rank-based daily thresholding protocol**: High Priority (Top 150 cells / ~5% of city), Moderate Priority (Ranks 151–300 / ~5%), and Baseline Risk (Ranks 301–3,026 / ~90%). The model was evaluated using a strict temporal holdout protocol on the historic 24-day September 2022 monsoon flood sequence ($E2022\\_09$), achieving a Precision-Recall Area Under Curve (PR-AUC) of **0.0026** against a random chance baseline of 0.0013 (**2.0× lift**), and capturing **25.0% of all confirmed historical flood days within its top 10% ranked cells** (**2.53× enrichment**).

The computational engine is served via an asynchronous **FastAPI** backend deployed on Render, coupled with an interactive cartographic **React + Vite** single-page web application deployed on Vercel. Spatial visualization is powered by a custom Leaflet Canvas vector rendering engine displaying all 3,026 cells at 60 FPS, complete with historical replay scrubbing, attribute inspection, spatial search, and a private **Telegram demonstration bot** interface. The project establishes an accessible, reproducible academic proof-of-concept for data-scarce urban flood susceptibility analysis while enforcing rigorous non-operational scientific disclaimers.

**Keywords**: Urban Flood Susceptibility Mapping, Machine Learning, XGBoost, Bengaluru Hydrology, Geospatial Data Science, Topographic Wetness Index, Height Above Nearest Drainage, CHIRPS Precipitation, Class Imbalance, FastAPI, React Leaflet.

---

## TABLE OF CONTENTS

- **Front Matter**
  - Academic Submission & Project Identity
  - Abstract
  - Table of Contents
  - List of Figures
  - List of Tables
  - List of Abbreviations
- **Chapter 1: Introduction**
  - 1.1 Background
  - 1.2 Urban Flooding in Bengaluru
  - 1.3 Role of Machine Learning in Flood Susceptibility Assessment
  - 1.4 Motivation
  - 1.5 Project Objectives
  - 1.6 Scope and Operational Boundaries
  - 1.7 Organization of the Report
- **Chapter 2: Literature Review**
  - 2.1 Urban Flooding and Susceptibility Mapping
  - 2.2 Machine Learning in Flood Susceptibility Assessment
  - 2.3 Rainfall Data and Urban Hydrology in Bengaluru
  - 2.4 Bengaluru-Specific Flood Assessment Research
  - 2.5 Technology-Enabled Flood Information Systems
  - 2.6 Comparative Analysis of Reviewed Literature
  - 2.7 Research Gap and Project Motivation
- **Chapter 3: Problem Statement and Requirements**
  - 3.1 Problem Statement
  - 3.2 Analysis of Existing Approaches
  - 3.3 Proposed Approach
  - 3.4 Functional Requirements
  - 3.5 Non-Functional Requirements
  - 3.6 Project Scope and Scientific Constraints
- **Chapter 4: System Architecture and Design**
  - 4.1 System Overview
  - 4.2 Overall Architecture
  - 4.3 Data Pipeline Architecture
  - 4.4 Machine Learning Model Architecture
  - 4.5 Backend Architecture
  - 4.6 API Architecture and Contract Specifications
  - 4.7 Frontend Architecture
  - 4.8 Spatial Visualization Engine
  - 4.9 Historical Replay Architecture
  - 4.10 Telegram Integration Architecture
  - 4.11 Cloud Deployment Architecture
- **Chapter 5: Data and Methodology**
  - 5.1 Dataset Description and Provenance
  - 5.2 Spatial Representation and Grid Discretization
  - 5.3 Input Features and Hydrological Significance
  - 5.4 Data Preprocessing and Alignment
  - 5.5 Feature Engineering
  - 5.6 Model Selection Rationale
  - 5.7 Model Training Methodology
  - 5.8 Inference and Spatial Ranking Formulation
  - 5.9 Daily Risk Classification Protocol
  - 5.10 Historical Simulation Framework
  - 5.11 Evaluation Methodology and Metrics
  - 5.12 Methodological Limitations
- **Chapter 6: Project Implementation**
  - 6.1 Development Environment and Tooling
  - 6.2 Data Pipeline Implementation
  - 6.3 Machine Learning Model Implementation
  - 6.4 Backend Implementation
  - 6.5 Frontend Implementation
  - 6.6 API Integration and Client Service
  - 6.7 Historical Replay Implementation
  - 6.8 Telegram Demonstration Bot Implementation
  - 6.9 Cloud Deployment Implementation
  - 6.10 Security, Privacy, and Credential Isolation
- **Chapter 7: Results, Testing and Demonstration**
  - 7.1 Project Demonstration Overview
  - 7.2 Frontend User Interface Demonstration
  - 7.3 Model Holdout Validation Results
  - 7.4 Historical Replay Findings (September 2022 Benchmark)
  - 7.5 Backend Automated Testing Suite
  - 7.6 Telegram Demonstration Bot Verification
  - 7.7 Frontend Build and QA Verification
  - 7.8 Cloud Deployment Verification
  - 7.9 Results Interpretation and Scientific Rigor
  - 7.10 Comprehensive Technical Limitations
- **Chapter 8: Conclusion and Future Work**
  - 8.1 Conclusion
  - 8.2 Summary of Project Contributions
  - 8.3 Summary of Key Limitations
  - 8.4 Future Research Directions
- **References**

---

## LIST OF FIGURES

- **Figure 1**: Overall System Architecture of N²M Flood Prediction Model
- **Figure 2**: Data Ingestion and Feature Processing Pipeline
- **Figure 3**: XGBoost Training and Out-of-Sample Holdout Workflow
- **Figure 4**: Daily Inference and Susceptibility Ranking Logic
- **Figure 5**: FastAPI Backend Architecture and Core Subsystems
- **Figure 6**: Frontend Component Architecture and Visualization Engine
- **Figure 7**: Historical Replay Sequence and Daily Spatial Updating
- **Figure 8**: Telegram Demonstration Dispatch Sequence Diagram
- **Figure 9**: Cloud Deployment Architecture on Vercel and Render
- **Figure 10**: User Interaction and Research Navigation Flowchart
- **Figure 11**: Overview of the Interactive Cartographic Flood Map Interface
- **Figure 12**: Class Distribution of Historical Flood Positives (Seed vs. Buffer Expansion)
- **Figure 13**: Precipitation Profile of the September 2022 Monsoon Replay Window

---

## LIST OF TABLES

- **Table 1**: Comparative Literature Synthesis Matrix
- **Table 2**: Functional Requirements Specification
- **Table 3**: Non-Functional Requirements Specification
- **Table 4**: Complete REST API Endpoints Directory
- **Table 5**: Primary Geospatial and Hydrometeorological Datasets
- **Table 6**: Complete Feature Set (18 Input Variables)
- **Table 7**: Historical Flood Events and Positive Label Breakdown
- **Table 8**: XGBoost Hyperparameter Configuration
- **Table 9**: Daily Susceptibility Tier Thresholds
- **Table 10**: Empirical Holdout Evaluation Metrics (September 2022 Holdout)
- **Table 11**: Software Dependencies and Development Environment
- **Table 12**: Automated Backend Test Suite Execution Results

---

## LIST OF ABBREVIATIONS

- **AHP**: Analytic Hierarchy Process
- **API**: Application Programming Interface
- **ARF**: Areal Reduction Factor
- **ASGI**: Asynchronous Server Gateway Interface
- **BBMP**: Bruhat Bengaluru Mahanagara Palike
- **CFRI**: Composite Flood Risk Index
- **CHIRPS**: Climate Hazards Center InfraRed Precipitation with Stations
- **CORS**: Cross-Origin Resource Sharing
- **DEM**: Digital Elevation Model
- **ESA**: European Space Agency
- **EWS**: Early Warning System
- **FSM**: Flood Susceptibility Mapping
- **GIS**: Geographic Information System
- **HAND**: Height Above Nearest Drainage
- **IDF**: Intensity–Duration–Frequency
- **IoT**: Internet of Things
- **KC Valley**: Koramangala–Challaghatta Valley
- **KSNDMC**: Karnataka State Natural Disaster Monitoring Centre
- **LULC**: Land Use / Land Cover
- **MCDA**: Multi-Criteria Decision Analysis
- **ML**: Machine Learning
- **MSL**: Mean Sea Level
- **NSFR**: Normalized Static Flood Risk
- **ODbL**: Open Database License
- **OSM**: OpenStreetMap
- **PR-AUC**: Precision-Recall Area Under Curve
- **QPF**: Quantitative Precipitation Forecast
- **REST**: Representational State Transfer
- **RF**: Random Forest
- **ROC-AUC**: Receiver Operating Characteristic Area Under Curve
- **RTFAI**: Real-Time Flood Alert Index
- **SPA**: Single Page Application
- **SRTM**: Shuttle Radar Topography Mission
- **SVM**: Support Vector Machine
- **SWMM**: Storm Water Management Model
- **TWI**: Topographic Wetness Index
- **UFSM**: Urban Flood Susceptibility Mapping
- **UI/UX**: User Interface / User Experience
- **USGS**: United States Geological Survey
- **XGBoost**: Extreme Gradient Boosting
"""
