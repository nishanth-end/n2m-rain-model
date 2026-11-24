"""
N²M Flood Prediction Model — Chapters 1 to 3
===========================================
"""

CHAPTERS_1_TO_3_MD = r"""# CHAPTER 1 — INTRODUCTION

### 1.1 Background
Urban flooding has emerged as one of the most destructive and frequent natural hazards confronting contemporary metropolitan centers across the globe [1]. Unlike riverine flooding, which is typically characterized by gradual water level rise along major alluvial floodplains over days or weeks, urban pluvial flooding is sudden, localized, and profoundly exacerbated by anthropogenic alterations to the natural landscape [2]. The rapid conversion of permeable vegetative soils into impermeable asphalt and concrete drastically reduces rainfall infiltration capacity, increases surface runoff volumes by factors of four to ten, and dramatically compresses hydrological lag times [1], [4]. In rapidly growing global South metropolises, this rapid surface modification frequently outpaces the expansion and maintenance of underground stormwater drainage infrastructure, transforming roadways and residential valleys into de facto drainage conduits during intense convective downpours [3], [6].

### 1.2 Urban Flooding in Bengaluru
Greater Bengaluru (administered by the Bruhat Bengaluru Mahanagara Palike — BBMP), situated at an average elevation of approximately 900 to 960 meters above mean sea level on the Deccan Plateau of Karnataka, India, presents a unique and precarious hydrometeorological profile [3], [5]. Geographically, the city spans a prominent topographical ridge partitioned across three primary drainage catchments: the **Hebbal Valley** draining northward, the **Vrishabhavathi Valley** draining westward and southward into the Arkavathi River system, and the **Koramangala–Challaghatta (KC) Valley** draining eastward and southward toward the Dakshina Pinakini River basin [5].

Historically, Bengaluru possessed no major natural perennial river. To sustain human settlement and agricultural irrigation in this semi-arid upland environment, medieval dynasties (principally founded under Kempe Gowda I in the 16th century and expanded under subsequent administrations) constructed a sophisticated hydrological infrastructure consisting of hundreds of cascading, man-made lakes (*keres*) [5], [6]. These interconnected water bodies were linked by open, gravity-fed stormwater drainage channels known locally as *rajakaluves*. During monsoon downpours, excess runoff from an upstream lake would overflow through a *rajakaluve* into the next downstream lake in the cascade, naturally mitigating flood peaks and recharging the underlying aquifer [6].

However, the rapid transformation of Bengaluru into India's premier information technology and biotechnology hub from the 1980s onward triggered unprecedented and poorly regulated urban expansion. Satellite land-cover analyses indicate that built-up impervious surface cover escalated from less than 8% in 1973 to over 93% by 2020. This rampant densification resulted in the systemic encroachment, disconnection, and siltation of the cascade network:
1. **Cascade Fragmentation**: Dozens of historical lake beds were drained, filled, and built over for bus terminals, sports stadiums, and commercial developments, severing the natural retention chain.
2. **Stormwater Channel Constriction**: *Rajakaluves* were frequently narrowed, diverted through right-angle concrete culverts, or converted into open municipal sewage conduits, drastically curtailing their hydraulic discharge capacity.
3. **Valley Encroachment**: Dense corporate IT tech parks, residential gated layouts, and arterial highways (notably the Eastern Outer Ring Road corridor between Silk Board and Marathahalli) were constructed directly across natural floodplains and low-lying agricultural valleys.

Superimposed upon this fragile built environment is the meteorological reality of Bengaluru's monsoon climate. Convective storm cells during the pre-monsoon (April–May) and post-monsoon (September–November) seasons frequently generate extreme localized downpours, often referred to colloquially as cloudbursts. Studies on Bengaluru's urban precipitation demonstrate that storms dropping 70 to 120 mm of rain within 60 to 90 minutes are common, yet exhibit extreme spatial heterogeneity [3]. A severe convective downpour can inundate arterial underpasses in Bellandur and Mahadevapura while northern neighborhoods in Yelahanka or Hebbal experience negligible precipitation [3]. Under these conditions, the absence of micro-catchment spatial differentiation in civic warnings leaves residents, civic engineers, and emergency responders without actionable intelligence.

### 1.3 Role of Machine Learning in Flood Susceptibility Assessment
To address the shortcomings of traditional physical modeling, machine learning (ML) has emerged as a powerful paradigm in environmental hazard mapping [1], [2]. Historically, urban flood predictions relied predominantly on complex hydrodynamic models such as the Storm Water Management Model (SWMM) or 2D shallow-water numerical solvers (e.g., MIKE FLOOD, HEC-RAS). While physically rigorous, hydrodynamic models require exhaustive parameterization, including high-resolution underground pipe geometries, invert elevations, roughness coefficients, culvert dimensions, and continuous real-time boundary inflows [1]. In rapidly expanding urban centers like Bengaluru, accurate subterranean pipe maps are largely incomplete, unmaintained, or fragmented across disparate municipal agencies. Furthermore, running multi-dimensional hydrodynamic simulations across 711 km² of urban terrain requires substantial compute time, rendering them computationally prohibitive for rapid exploratory screening and continuous daily spatial updating [2], [4].

Machine learning models, particularly tree-based ensemble architectures such as Extreme Gradient Boosting (**XGBoost**) and Random Forests, offer a compelling alternative [2]. By extracting non-linear statistical associations between historical flood occurrences, high-resolution static terrain indicators (elevation, slope, topographic wetness, distance to hydrographic networks), and dynamic precipitation saturation matrices, machine learning models can evaluate spatial vulnerability across thousands of land parcels within milliseconds [1], [2]. 

However, applying machine learning to urban flood assessment presents severe methodological challenges that are frequently overlooked in contemporary academic literature [2]:
- **Extreme Class Imbalance**: True, confirmed flood incidences are exceedingly sparse in time and space, typically comprising less than 0.1% of all monitored land units during a monsoon season.
- **Uncalibrated Model Probabilities**: Severe class imbalance causes raw predicted probabilities from algorithms like XGBoost to cluster near zero (rarely exceeding 0.25 to 0.35), making standard classification cutoffs (such as $P \ge 0.5$) mathematically invalid and practically useless.
- **Spatial Autocorrelation and Leakage**: Naive random spatial cross-validation can inadvertently allow training algorithms to memorize specific geographic centroids rather than learning genuine hydrological relationships.
- **Scientific Misrepresentation**: Many studies incorrectly conflate relative *flood susceptibility* (the physical spatial predisposition of land to accumulate water) with calibrated *flood probability* or deterministic *water depth forecasting*, creating dangerous false precision [2].

### 1.4 Motivation
The motivation for this engineering project arises directly from the catastrophic monsoon flood event of **September 2022 (Event $E2022\\_09$)** in Bengaluru. Following days of persistent antecedent rainfall culminating in severe downpours on September 4–5, 2022, major sectors of the eastern IT corridor—including Bellandur, Yamalur, Rainbow Drive, RMZ Ecospace, and the Outer Ring Road—experienced catastrophic inundation. High-tech campuses, international tech hubs, residential villas, and major arterial routes were submerged under 1 to 2.5 meters of water, causing estimated economic damages exceeding billions of Indian rupees and requiring the deployment of motorized life rafts and earthmovers to evacuate IT professionals and residents.

Post-disaster municipal audits revealed a profound information asymmetry: civic authorities possessed meteorological reports indicating city-level rainfall, but had no accessible, high-resolution spatial decision-support platform capable of prioritizing which micro-catchments faced imminent hydrological overflow based on terrain vulnerability and antecedent soil saturation.

Recognizing this gap, our student team—Nishanth G M, Mohith M, and Nihal Rao (collectively designated **N²M**)—sought to build an end-to-end, reproducible, and scientifically grounded engineering research platform. The goal was to prove that open-access geospatial terrain data (NASA/USGS SRTM, OpenStreetMap, ESA WorldCover) coupled with daily satellite-gauge precipitation records (CHIRPS) could power an explainable, data-driven machine learning system to deliver daily spatial susceptibility rankings across all 198 wards of Bengaluru.

### 1.5 Project Objectives
The specific engineering and research objectives of the N²M Flood Prediction Model project are:
1. **Geospatial Mesh Discretization**: Partition the 711.59 km² urban territory of Greater Bengaluru into a continuous, uniform spatial grid of **3,026 discrete cells** (~500 m × 500 m resolution, 0.25 km² per cell) covering all 198 BBMP administrative wards.
2. **Hydrological & Terrain Feature Engineering**: Extract and compute 10 static terrain and built-environment indices per cell, including mean elevation, slope, Topographic Wetness Index (TWI), Height Above Nearest Drainage (HAND), upstream flow accumulation, impervious surface fraction, lake cascade density, and Euclidean distances to lakes, stormwater channels (*rajakaluves*), and arterial roads.
3. **Meteorological Feature Integration**: Design and implement a dynamic multi-scale precipitation processing pipeline that links each grid cell to its corresponding Climate Hazards Center CHIRPS precipitation pixel, deriving 8 multi-day rolling sums and antecedent lag features (`rain_1d`, `rain_3d`, `rain_7d`, `rain_14d`, `rain_30d`, `rain_lag1`, `rain_lag2`, `rain_lag3`).
4. **Machine Learning Model Formulation**: Develop an extreme gradient-boosted decision tree classifier (**XGBoost**) parameterized to handle extreme class imbalance (`scale_pos_weight = 89.16`) to score daily cell susceptibility.
5. **Operational Rank-Based Thresholding Protocol**: Replace arbitrary uncalibrated probability thresholds with a defensible, daily dense ranking protocol that classifies cells into actionable relative operational tiers: **High Priority** (Top 150 cells / ~5% of city), **Moderate Priority** (Ranks 151–300 / ~5%), and **Baseline Risk** (Ranks 301–3,026 / ~90%).
6. **Strict Out-of-Sample Holdout Evaluation**: Validate the model using a sequestered temporal holdout protocol on the historic 24-day September 2022 monsoon flood sequence ($E2022\\_09$), ensuring the evaluation model never observes any data or labels from that event during training.
7. **Full-Stack Cartographic Dashboard Development**: Implement an asynchronous **FastAPI** backend coupled with an interactive **React + Vite** single-page web dashboard, utilizing a custom Leaflet Canvas rendering engine to visualize all 3,026 cells at 60 FPS with full historical replay, cell inspection, spatial filtering, and cell search capabilities.
8. **Private Telegram Demonstration Bot**: Integrate a token-safe, server-side Telegram demonstration interface allowing authorized project evaluators to query system status and trigger demonstration alert bulletins.
9. **Cloud Deployment on Free-Tier Infrastructure**: Containerize and deploy the decoupled architecture on cloud platforms (**Vercel** for frontend, **Render** for backend) within free-tier resource constraints (<512 MB RAM), ensuring high availability and zero credential leakage.
10. **Comprehensive Limitations and Scientific Boundaries**: Formally document the boundary conditions of the system, enforcing clear scientific disclaimers that outputs represent empirical relative rankings rather than certified emergency alerts or calibrated flood probabilities.

### 1.6 Scope and Operational Boundaries
To maintain rigorous scientific and academic integrity, the project explicitly defines what the N²M Flood Prediction Model **is** and what it **is not**:
- **What It IS**: An academic proof-of-concept and geospatial research platform demonstrating relative spatial prioritization among 3,026 urban parcels during monsoon rainfall events.
- **What It IS NOT**: It is **not** an operational municipal early warning system, **not** a calibrated probabilistic forecast, **not** an inundation depth model (it does not predict water depth in meters), and **not** a replacement for 2D hydrodynamic simulations or municipal emergency directives.

### 1.7 Organization of the Report
The remainder of this report is organized as follows:
- **Chapter 2 (Literature Review)** provides a thematic, comparative analysis of recent peer-reviewed literature in urban flood susceptibility mapping, machine learning in hydrology, Bengaluru-specific rainfall studies, and digital disaster systems, establishing the formal research gap.
- **Chapter 3 (Problem Statement and Requirements)** formally specifies the engineering problem statement, analyzes existing approaches, and outlines functional and non-functional system requirements.
- **Chapter 4 (System Architecture and Design)** presents the high-level system architecture, data pipeline, ML engine, backend service components, API contracts, frontend architecture, and cloud deployment topology.
- **Chapter 5 (Data and Methodology)** details dataset provenance, the 3,026-cell spatial discretization, the 18 engineered features, XGBoost training formulation, rank-based thresholding, and holdout validation protocols.
- **Chapter 6 (Project Implementation)** documents the software stack, data pipeline code, backend route implementation, Leaflet Canvas rendering engine, Telegram bot service, and security configurations.
- **Chapter 7 (Results, Testing and Demonstration)** presents empirical holdout validation results, the 82-test automated backend test suite, frontend build QA, historical replay findings for September 2022, and comprehensive technical limitations.
- **Chapter 8 (Conclusion and Future Work)** synthesizes project contributions, summarizes boundary conditions, and outlines prospective research directions.
- **References** provides a complete, numbered bibliography formatted according to IEEE standards with verified Digital Object Identifiers (DOIs).

---

# CHAPTER 2 — LITERATURE REVIEW

### 2.1 Urban Flooding and Susceptibility Mapping
Urban flood susceptibility mapping (UFSM) has developed rapidly over the last two decades as urban planners and hydrologists seek scalable tools to identify areas predisposed to flooding [1]. In their comprehensive systematic review, Islam et al. (2025) synthesize the global evolution of flood susceptibility mapping methodologies, documenting how the field has transitioned from manual multi-criteria decision analysis (MCDA) toward remote sensing integration and machine learning algorithms [1]. The authors emphasize that urban flooding is fundamentally driven by the compounding effects of climate change, rapid impervious surface expansion, and overburdened drainage networks. 

Islam et al. (2025) evaluate the most frequently utilized flood-conditioning parameters across 140+ international studies, revealing that elevation, slope, Topographic Wetness Index (TWI), Land Use/Land Cover (LULC) imperviousness, and distance to hydrographic networks constitute the core conditioning feature set in over 85% of successful susceptibility mapping frameworks [1]. The review establishes that while hydrodynamic 1D/2D models (such as SWMM and HEC-RAS) provide physical fidelity regarding velocity and depth, their operational utility is severely hindered by extreme computational latency and exhaustive data requirements. Consequently, remote sensing and data-driven GIS models have become indispensable for full-city baseline risk assessments, especially in developing metropolises where underground drainage telemetry is absent [1].

### 2.2 Machine Learning in Flood Susceptibility Assessment
Pourzangbar et al. (2025) present a critical, decade-spanning (2013–2023) state-of-the-art review analyzing the utilization of machine learning architectures in flood susceptibility mapping [2]. Their analysis identifies significant methodological divergences across published literature, noting that many studies rely on subjective trial-and-error procedures for feature selection, hyperparameter tuning, and model validation. 

A central finding of Pourzangbar et al. (2025) is the consistent superiority of tree-based ensemble algorithms—specifically Random Forests (RF) and Extreme Gradient Boosting (XGBoost)—over individual classifiers such as Support Vector Machines (SVM), Multi-Layer Perceptrons (MLP), and Naive Bayes [2]. Tree ensembles naturally accommodate non-linear feature interactions, exhibit robustness to multicollinearity among topographic indices (e.g., elevation and slope), and provide explicit feature importance metrics that enhance model interpretability. 

Crucially, Pourzangbar et al. (2025) highlight a pervasive vulnerability in contemporary ML flood literature: the improper handling of extreme class imbalance and spatial autocorrelation [2]. Because historical flood inventories contain far fewer flooded points than non-flooded terrain, naive sampling often causes models to overfit on majority dry classes or to produce uncalibrated probabilities that cluster near zero. The authors advocate for explicit class-weighting parameters, rigorous out-of-sample spatial or temporal validation, and realistic performance metrics (such as Precision-Recall Area Under Curve [PR-AUC]) rather than relying solely on Receiver Operating Characteristic (ROC-AUC), which can be misleadingly inflated in extreme class imbalance regimes [2].

### 2.3 Rainfall Data and Urban Hydrology in Bengaluru
A critical prerequisite for modeling urban flooding is accurate hydrometeorological input. In their pioneering study on Bengaluru's urban rainfall regime, Joseph, Mujumdar, and Das Bhowmik (2022) investigate the spatiotemporal variability of extreme rainfall across Greater Bengaluru [3]. The authors highlight that historical long-term precipitation monitoring in Bengaluru was historically constrained to only two primary ground observatories maintained by the India Meteorological Department (IMD)—Bangalore City station and HAL Airport station. Only in recent years did the Karnataka State Natural Disaster Monitoring Centre (KSNDMC) establish a dense urban network of telemetric rain gauges across BBMP wards [3].

Using machine learning (Random Forest regression), Joseph et al. (2022) reconstructed historical sub-daily precipitation time series across the city dating back to 1969 [3]. Their research yielded two findings of fundamental importance to our project:
1. **Extreme Spatial Heterogeneity**: Intensity–Duration–Frequency (IDF) relationships exhibited marked spatial divergence across different sectors of the city. Convective storms in Bengaluru frequently display localized storm cells that dump intense rainfall over a 5 to 10 km radius while leaving adjacent wards unaffected.
2. **Areal Reduction Factor (ARF) Decay**: The study observed a substantial drop in Areal Reduction Factors as the catchment area exceeded 450 km², indicating that peak storm intensities over small micro-catchments (such as 0.25 km² cells) are substantially diluted when averaged across city-scale administrative boundaries [3].

These findings mathematically validate the premise of the N²M project: modeling urban flood risk in Bengaluru using a single citywide rainfall metric is scientifically unsound. An accurate system must allocate rainfall dynamically across localized spatial sectors.

### 2.4 Bengaluru-Specific Flood Assessment Research
Recent academic investigations have examined the localized impacts of flooding in specific sectors of Bengaluru, providing vital regional ground truth:

Pathak, Mathad, and Gagnon (2025) conducted an extensive empirical study in Bengaluru's flood-prone **Koramangala–Challaghatta (KC) Valley**, investigating urban flood damage across residential and commercial sectors [5]. Through household surveys and Random Forest regression modeling, the authors analyzed stage-damage functions to quantify the relationship between flood depth, property values, structural characteristics, and direct economic losses [5]. Their findings revealed that while flood depth is the primary physical driver of damage across all sectors, commercial tech parks along the Outer Ring Road exhibit higher adaptive capacity (installing floodwalls, dewatering pumps, and elevated substations) compared to unorganized residential neighborhoods, which suffer severe unmitigated structural losses [5]. Pathak et al. (2025) emphasize a critical terminological distinction essential to our academic report: **flood susceptibility** (the physical predisposition of a parcel to accumulate water based on terrain and rain) must not be conflated with **vulnerability** (the degree of loss resulting from a hazard), **exposure** (the inventory of assets in the hazard zone), or **damage** (the monetary loss incurred).

Focusing on the municipal ward scale, Mukhopadhyay and Das (2026) developed a **Composite Flood Risk Index (CFRI)** framework tailored specifically for **Bellandur Ward (Ward 150)**, the central locus of Bengaluru's 2022 flood crisis [6]. The authors coupled a Normalized Static Flood Risk (NSFR) index—derived through Multi-Criteria Decision Analysis (MCDA) across 24 indicators spanning hazard, exposure, vulnerability, and governance—with a dynamic Real-Time Flood Alert Index (RTFAI) modified by an urban drainage amplification factor ($\\alpha = 1.2$). Their empirical evaluation determined that Bellandur Ward has a static risk score of 0.89 (signaling critical baseline structural vulnerability) and that composite risk exceeded 1.0 during the peak monsoon events of September 2022 [6]. Mukhopadhyay and Das (2026) demonstrated that Bellandur's flooding is driven by an overburdened drainage bottleneck where runoff from upstream catchments converges on encroached lake channels.

### 2.5 Technology-Enabled Flood Information Systems
The integration of digital platforms, cloud computing, and real-time communication for flood disaster management has been reviewed comprehensively by Al-Rawas et al. (2024) [4] and Pham Ngoc Thinh (2025) [7]. 

Al-Rawas et al. (2024) analyze emerging technologies across artificial intelligence, Internet of Things (IoT), cloud computing, and robotics [4]. Their systematic analysis of 2010–2023 literature reveals that AI/ML models represent 64% of recent predictive innovations, while IoT and cloud architectures represent 19% and 6%, respectively. The authors argue that predictive machine learning models fail to protect communities if their outputs remain siloed in offline research repositories; effective disaster mitigation requires automated deployment pipelines, cloud-hosted API gateways, and intuitive map visualizations accessible to decision-makers [4]. However, they warn that many IoT and cloud-based systems suffer from single points of failure, network disconnections during extreme weather events, and uncalibrated models that generate frequent false alarms.

Pham Ngoc Thinh (2025) reviews Early Warning Systems (EWS) as non-structural urban resilience mechanisms, utilizing the PRISMA methodology across 40+ international studies [7]. The review underscores that technical modeling accuracy must be paired with clear, multi-tiered communication strategies. In low-resource urban settings, complex probabilistic distributions often confuse end-users; systems that translate technical scores into unambiguous, priority-based operational alert tiers (e.g., High, Moderate, Baseline) achieve significantly higher adherence and response efficiency [7].

Complementing these software frameworks, Arshad et al. (2019) examine the role of computer vision, CCTV camera feeds, and wireless sensor networks in real-time flood mapping and water-level tracking [8]. Their survey illustrates how automated vision algorithms can extract water levels from urban infrastructure cameras, highlighting a valuable future data-collection pathway to validate and enrich sparse historical flood labels in rapidly urbanizing regions.

### 2.6 Comparative Analysis of Reviewed Literature
Table 1 synthesizes the reviewed literature, contrasting study objectives, geographic scope, modeling methodologies, key findings, and their precise relevance and distinction relative to the N²M project.

**Table 1: Comparative Literature Synthesis Matrix**

| Study & Citation | Geographic Region | Core Methodology | Key Findings & Insights | Relevance to N²M Framework | Distinction / Limitation vs. N²M |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Islam et al. (2025)** [1]<br>*Remote Sensing* | Global Urban Centers | PRISMA Systematic Review of RS & ML UFSM literature | Elevation, slope, TWI, and LULC are the top conditioning features; ML outpaces 2D hydraulic models in spatial screening speed. | Justifies N²M's 18-feature topographic & built environment design. | Global review; does not implement an operational pipeline for an Indian city. |
| **Pourzangbar et al. (2025)** [2]<br>*J. Flood Risk Mgmt.* | Global Catchments (2013–2023) | Comparative analysis of ML architectures in FSM | Tree ensembles (RF, XGBoost) offer optimal accuracy and explainability; class imbalance is frequently mishandled. | Directly justifies XGBoost selection and `scale_pos_weight = 89.16` tuning in N²M. | Emphasizes probabilistic modeling rather than daily rank-based operational thresholding. |
| **Joseph et al. (2022)** [3]<br>*Water* | Bengaluru, Karnataka, India | Random Forest regression for sub-daily rainfall reconstruction | Intra-city rainfall exhibits extreme spatial variability; ARF drops sharply above 450 km². | Empirically confirms that Bengaluru cannot be modeled with a single rain gauge; validates N²M's 37 CHIRPS pixels. | Focuses on rainfall series reconstruction rather than flood inundation or spatial susceptibility mapping. |
| **Al-Rawas et al. (2024)** [4]<br>*Water* | Global Flash Flood Basins | Review of AI, IoT, Cloud, and Robotics technologies | AI/ML represents 64% of innovations; cloud-hosted GIS platforms enable real-time dissemination. | Validates N²M's decoupled cloud deployment (Vercel + Render) and messaging bot integration. | Highlights that cloud systems often lack local ground-truth calibration in developing countries. |
| **Pathak et al. (2025)** [5]<br>*Natural Hazards* | KC Valley, Bengaluru, India | Household surveys + Random Forest damage functions | Flood depth dictates losses; residential damage scales with asset value, while commercial entities deploy adaptive defenses. | Provides deep local context on the KC Valley; clarifies terminology (susceptibility vs. damage). | Focuses on socioeconomic financial loss functions, whereas N²M models physical terrain susceptibility. |
| **Mukhopadhyay & Das (2026)** [6]<br>*ETASR* | Bellandur Ward (Ward 150), Bengaluru | Multi-Criteria Decision Analysis (MCDA) + Static/Real-time index | Evaluates Bellandur NSFR at 0.89; CFRI exceeded 1.0 during September 2022 peak rainfall. | Validates N²M's identification of Ward 150 (Cell 722) as the top citywide susceptibility hotspot. | Index-based weighted scoring (MCDA) based on 24 manual criteria; N²M uses data-driven gradient boosted trees. |
| **Pham Ngoc Thinh (2025)** [7]<br>*Rev. Agric. Sci.* | Developing World Urban Centers | PRISMA review of EWS non-structural measures | Institutional communication gaps cause EWS failures; urges clear risk tiers over raw probabilities. | Informs N²M's rank-based alert tiers (High/Moderate/None) and Telegram bulletin design. | Qualitative review of EWS governance and resilience frameworks. |
| **Arshad et al. (2019)** [8]<br>*Sensors* | Global Sensor Deployments | Systematic review of IoT and computer vision | Wireless sensor networks and camera feeds can validate flood presence in real-time. | Informs future data collection pipelines to address N²M's ground-truth label sparsity. | Physical sensor hardware and image processing review; outside N²M's software scope. |

### 2.7 Research Gap and Project Motivation
A synthesis of the international and regional literature reveals a pronounced academic and engineering gap:
1. **The Hydrodynamic vs. Index Dilemma**: Engineering authorities in Bengaluru are forced to choose between computationally prohibitive, data-starved 2D hydrodynamic simulations (SWMM) or subjective, manually weighted multi-criteria decision indices (AHP/MCDA) that cannot dynamically adapt to non-linear storm saturation.
2. **The Class-Imbalance & Spatial Neglect in ML Studies**: Published machine learning flood papers frequently treat susceptibility prediction as an abstract classification task evaluated on artificially balanced, randomly split test sets, generating unrealistically high ROC-AUC metrics while ignoring extreme real-world class imbalance (in our study, 1 positive cell-day per 7,350 cell-days). Furthermore, they rarely test their models on strict, sequestered out-of-sample historical storm events.
3. **The Deployment Disconnect**: Predictive models developed in academic literature almost universally remain as isolated Python scripts or Jupyter notebooks, lacking integration into interactive, high-performance spatial dashboards or automated messaging protocols that civic evaluators can explore in real time.

**The N²M Contribution**:
The N²M Flood Prediction Model explicitly bridges this gap. It implements an open-source, fully reproducible engineering system that couples a uniform 3,026-cell geospatial skeleton with an explainable XGBoost model trained with class-imbalance weighting (`scale_pos_weight = 89.16`). It introduces an operational daily dense-ranking thresholding protocol, validates the framework strictly out-of-sample on the historic September 2022 monsoon event ($E2022\\_09$), and deploys the entire workflow onto modern cloud infrastructure (FastAPI on Render, React + Leaflet Canvas on Vercel, and automated Telegram demonstration dispatch) with transparent scientific disclaimers.

---

# CHAPTER 3 — PROBLEM STATEMENT AND REQUIREMENTS

### 3.1 Problem Statement
The formal engineering problem addressed in this project is defined as follows:

> **Problem Statement**:  
> To design, construct, evaluate, and deploy an automated, end-to-end geospatial machine learning platform that ingests multi-source terrain morphology indices and dynamic satellite precipitation grids to generate reproducible daily relative flood susceptibility rankings across a uniform 500 m spatial grid covering Greater Bengaluru, and to serve these spatial analytics through an interactive web cartographic dashboard and automated messaging interface within free-tier cloud constraints.

### 3.2 Analysis of Existing Approaches
Urban flood risk assessment in Indian metropolises currently relies on three broad paradigms, each characterized by operational trade-offs:
1. **City-Scale Municipal Flood Bulletins**: Issued by municipal agencies (BBMP, KSNDMC) based on district weather advisories. These advisories provide citywide warnings (e.g., "Heavy rainfall expected across Bengaluru Urban"), offering zero spatial granularity to differentiate between high-ridge neighborhoods (e.g., Sadashivanagar) and severely depressed lake valley basins (e.g., Bellandur or HSR Layout).
2. **Deterministic 1D/2D Hydrodynamic Modeling**: Implemented using software suites like EPA SWMM, MIKE Urban, or TUFLOW. While hydraulically precise, these models require exhaustive inputs (pipe diameters, culvert silt levels, invert elevations) that are largely unmapped across Bengaluru's informal settlements, and require hours of compute time per simulation, preventing continuous daily citywide screening.
3. **Static Indicator-Based Vulnerability Indices (AHP / MCDA)**: Derived by assigning fixed subjective weights to factors such as slope, drainage density, and road proximity. While computationally fast, these static indices cannot ingest dynamic precipitation matrices or model complex non-linear saturation thresholds.

### 3.3 Proposed Approach
The N²M Flood Prediction Model proposes a middle-path engineering architecture:
- **Spatial Grid Discretization**: Partition Bengaluru into 3,026 uniform cells (500 m × 500 m), providing micro-catchment resolution without overwhelming database memory.
- **Explainable Machine Learning**: Train an XGBoost gradient-boosted decision tree classifier that ingests 10 static terrain features and 8 dynamic rolling precipitation indices.
- **Daily Relative Rank Prioritization**: Avoid uncalibrated probability cutoffs by evaluating daily relative ranks, designating the top 5% of cells as High Priority and the next 5% as Moderate Priority.
- **Decoupled Modern Web Architecture**: Serve precomputed historical replay slices and model inferences via a high-performance asynchronous FastAPI REST backend, consumed by a React Single Page Application utilizing a custom Leaflet Canvas vector rendering engine.

### 3.4 Functional Requirements
The functional requirements of the system, verified through implementation and automated testing, are presented in Table 2.

**Table 2: Functional Requirements Specification**

| Requirement ID | Module | Functional Description | Verification Status |
| :--- | :--- | :--- | :--- |
| **FR-01** | Data Pipeline | The system shall discretize the BBMP urban boundary into 3,026 uniform spatial cells (~500m × 500m) and link each to its nearest CHIRPS rainfall pixel. | Verified (`cells_static.csv`, `cell_pixel_map.csv`) |
| **FR-02** | Feature Engine | The system shall compute 10 static terrain indicators and 8 dynamic multi-day precipitation rolling sums and lag matrices per cell. | Verified (`features.json`, 18 features validated) |
| **FR-03** | Model Inference | The system shall load the sequestered XGBoost model (`flood_xgb_holdout_E2022_09.json`) and score 3,026 cells for any requested date within <100 ms. | Verified (`score_cells.py`, FastAPI backend) |
| **FR-04** | Rank Thresholding | The system shall calculate daily dense ranks (1 to 3,026) and assign High (Top 150), Moderate (Ranks 151–300), and Baseline (Ranks 301–3,026) tiers. | Verified (`thresholds.json`, API routes) |
| **FR-05** | Historical Replay | The system shall provide interactive sequential replay across all 24 dates of the September 2022 monsoon event (2022-08-22 to 2022-09-14). | Verified (`/api/dates`, `/api/risk`, Replay engine) |
| **FR-06** | Spatial Filtering | The system shall allow users to filter rendered map cells by priority tier (`ALL`, `HIGH_MOD`, `HIGH_ONLY`) and search for any cell by ID (0 to 3,025). | Verified (`FloodMapPage.jsx`, Canvas engine) |
| **FR-07** | Cell Inspector | The system shall display physical terrain attributes (elevation, slope, HAND, TWI, impervious fraction) and daily rank for any selected grid cell. | Verified (Telemetry Inspector Drawer) |
| **FR-08** | Telegram Bot | The system shall support a private Telegram demonstration bot responding to `/start`, `/help`, `/status`, and `/demo [date]` commands for authorized users. | Verified (`telegram_service.py`, Webhook handler) |
| **FR-09** | Dispatch Safety | Outbound Telegram demo alerts shall be strictly restricted to whitelisted evaluator chat IDs (`is_authorized` check) with token redaction. | Verified (`test_telegram_service.py`) |
| **FR-10** | Cloud Resilience | The backend shall expose a `/health` endpoint for cloud load balancers and support CORS for deployed Vercel frontend origins. | Verified (`backend/main.py`, Render probe) |

### 3.5 Non-Functional Requirements
The non-functional performance and operational criteria are detailed in Table 3.

**Table 3: Non-Functional Requirements Specification**

| Requirement ID | Category | Performance Target & Specification | Verified Implementation |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Usability | Intuitive GIS interface with cartographic visual hierarchy; color-coded susceptibility tiers conforming to cartographic conventions. | Custom modern UI with restrained editorial theme, responsive layout, and floating inspectors. |
| **NFR-02** | Render Performance | Web map vector layer must render all 3,026 grid cell markers at 60 FPS without browser DOM freezing or memory leaks. | Custom Leaflet Canvas marker layer; viewport culling and single-batch redraw cycle. |
| **NFR-03** | API Latency | Replay data endpoints (`/api/risk`, `/api/summary`) must respond within <150 ms under local execution and <500 ms under cloud hosting. | Preloaded in-memory PyArrow Parquet slices; average local endpoint response latency is ~12 ms. |
| **NFR-04** | Memory Footprint | Backend resident memory must remain below 100 MB to safely operate within Render's free-tier limit of 512 MB RAM. | Full backend memory footprint is ~15–20 MB (<4% of free-tier allocation). |
| **NFR-05** | Security & Privacy | Bot tokens and evaluator chat IDs must remain strictly server-side; tokens must never appear in logs, git, or client bundles. | Token isolated in server environment variables; regex-sanitized in `telegram_service.py`. |
| **NFR-06** | Maintainability | Modular code separation between data loading, ML scoring, API routing, and frontend rendering, backed by automated unit tests. | Clean Python package structure with 82 passing tests and decoupled React Vite architecture. |

### 3.6 Project Scope and Scientific Constraints
The academic scope is governed by strict scientific boundary conditions:
1. **Severe Label Sparsity**: The entire training dataset contains only 240 positive cell-day labels across 1.76 million records, derived from approximately 10 documented flood locations expanded via a $3 \times 3$ grid buffer.
2. **Coarse Precipitation Resolution**: CHIRPS satellite rainfall operates at 0.05° (~5.3 km) daily resolution. It cannot resolve localized sub-hourly cloudbursts dropping 80 mm in 45 minutes over individual street underpasses.
3. **Absence of Subterranean Pipe Hydraulics**: The model possesses no structural knowledge of underground pipe diameters, siltation levels in stormwater culverts, or trash blockages in *rajakaluves*.
4. **Diagnostic Nowcast Nature**: In historical replay, rainfall features (`rain_1d`, `rain_3d`) are evaluated concurrently with the flood label on day $d$. In an operational forecasting setting, realized rainfall is unknown ahead of time; forecasting would require numerical weather prediction (NWP) precipitation forecasts.
5. **Non-Operational Academic Status**: Output scores represent relative daily rankings, **not** certified flood probabilities or civil defense alerts.
"""
