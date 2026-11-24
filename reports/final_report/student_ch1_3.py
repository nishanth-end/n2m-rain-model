"""
Undergraduate Student Project Report — Chapters 1 to 3
=====================================================
Tone: Clear, honest, well-written for second-year CSE students.
"""

CHAPTERS_1_TO_3 = r"""# CHAPTER 1 — INTRODUCTION

### 1.1 Background of Urban Flooding
Urban flooding is one of the most visible and disruptive challenges faced by rapidly growing cities around the world today. Unlike rural flooding, which often occurs when large rivers slowly overflow their banks during extended seasonal monsoons, urban flooding happens very quickly. In heavily built-up areas, rainwater cannot easily soak into the ground because the natural soil has been replaced by paved roads, concrete footpaths, residential complexes, and parking lots. 

When heavy rainfall hits an urban environment, surface runoff is generated almost immediately. If the city's drainage infrastructure cannot carry this sudden volume of water away fast enough, water quickly pools in low-lying roads, underpasses, and residential areas. The problem is made worse by localized, short-duration convective storms—often called cloudbursts or thunderstorm squalls—where a massive amount of rain falls over just one or two neighborhoods in less than an hour while neighboring parts of the same city remain completely dry.

Traditional methods for predicting floods depend heavily on complex physical and hydrodynamic simulations, such as the Storm Water Management Model (SWMM) or two-dimensional hydrodynamic models. While these engineering tools are accurate when complete civil engineering data is available, they require extensive, detailed parameters that are rarely available for every street in a developing metropolis. These required inputs include underground pipe cross-sections, pipe age, current silt levels, exact inlet positions, and local pump pumping rates. For a student mini-project or for an initial municipal overview, running full hydrodynamic equations across an entire city is computationally expensive and data-prohibitive.

### 1.2 Urban Flooding Challenges in Bengaluru
Bengaluru, the capital of Karnataka and the primary information technology hub of India, has experienced extraordinary physical growth over the last forty years. The municipal area governed by the Bruhat Bengaluru Mahanagara Palike (BBMP) spans approximately 711.59 square kilometers across 198 administrative wards. Historically, Bengaluru was built on an undulating plateau at an average elevation of around 900 meters above sea level, characterized by three major natural drainage valleys: the Hebbal Valley, the Koramangala–Challaghatta (KC) Valley, and the Vrishabhavathi Valley.

In past centuries, Bengaluru relied on a sophisticated, interconnected system of man-made lakes (*keres*) constructed across these valley cascades. When an upstream lake filled with monsoonal rainwater, surplus water overflowed through wide, natural open stormwater channels called *rajakaluves* into the next downstream lake. This historical design naturally buffered peak monsoon runoff and recharged local aquifers.

However, rapid urban expansion has severely disrupted this hydrological balance. Studies by ecological researchers at the Indian Institute of Science (IISc) have shown that the city's built-up impervious surface area expanded from less than 8% in 1973 to over 93% by 2020. During this construction boom:
1. Many smaller lakes were drained, leveled, or encroached upon to build bus terminals, residential layouts, and technology parks.
2. Natural stormwater drains (*rajakaluves*) were straightened, narrowed, concrete-walled, or blocked by construction debris and municipal solid waste.
3. Natural drainage paths connecting lakes were severed, turning formerly self-draining valleys into artificial basins where runoff easily accumulates.

During the monsoon seasons of recent years—most notably the catastrophic monsoon of September 2022—torrential rains caused widespread urban chaos. Critical tech corridors along the Outer Ring Road, prominent residential areas such as Koramangala and HSR Layout, and low-lying valleys in Bellandur and Varthur were submerged under several feet of water. Residents and local authorities faced severe disruption, vehicle damage, power outages, and business closures.

### 1.3 Why Machine Learning Helps in Flood Susceptibility Studies
Machine learning provides a practical, data-driven approach for studying urban flood patterns. Instead of attempting to calculate exact water depths through differential fluid dynamics equations, machine learning models can learn the statistical relationship between physical terrain features, historical rainfall patterns, and past flooding incidents.

In computer science, decision tree ensembles like **eXtreme Gradient Boosting (XGBoost)** are well known for handling structured, tabular data effectively. XGBoost can process multiple non-linear features—such as terrain slope, distance to the nearest stormwater drain, elevation above drainage lines, and multi-day accumulated rainfall—without requiring all data to follow a strict linear distribution.

By training on historical monsoonal weather records and past flooding locations, a machine learning model can assign an experimental susceptibility score to different neighborhoods. This allows researchers and local planners to identify which specific micro-catchments are inherently vulnerable during heavy rains, helping to prioritize on-the-ground drainage maintenance and resource deployment.

### 1.4 Motivation for the Project
As second-year undergraduate Computer Science and Engineering students studying in Bengaluru, we have directly witnessed how quickly monsoonal rain can paralyze traffic, submerge arterial roads, and disrupt daily student life. We frequently observed that municipal rainfall warnings are broadcasted as a single warning for the entire city or taluk (for example, "Heavy rain alert for Bengaluru Urban"). 

However, anyone living in Bengaluru knows that rainfall is not uniform across the city. A torrential thunderstorm may submerge roads in Bellandur or Marathahalli while Jayanagar or Malleshwaram sees only a light drizzle. Furthermore, even within a rainy sector, some streets flood every single monsoon while other streets just two blocks away drain immediately due to higher ground slope.

We were motivated to ask: *Can we, as computer science students, build a workable geospatial data pipeline and machine learning model that looks at open-source terrain data and rainfall estimates to highlight which specific areas of Bengaluru are most susceptible to waterlogging on any given rainy day?*

This question drove the design and implementation of the **N²M Flood Prediction Model** (named after group members Nishanth, Mohith, and Nihal).

### 1.5 Project Objectives
To address this challenge within the scope of our academic mini-project, we set five clear objectives:
1. **Develop an Automated Geospatial Data Pipeline**: Divide Greater Bengaluru into a standardized Cartesian grid of equal-sized cells and compute essential terrain, drainage, and built-environment metrics for each cell using open geospatial datasets.
2. **Integrate Dynamic Precipitation Data**: Link each spatial grid cell to historical and daily rainfall observations from satellite-gauge records (CHIRPS) and modern weather APIs to capture spatial rainfall variation across the city.
3. **Train an Imbalance-Aware Machine Learning Model**: Train an XGBoost classifier that handles the extreme rarity of confirmed flood records, producing a daily relative susceptibility score for each grid cell.
4. **Implement an Intuitive Daily Ranking System**: Develop an operational ranking mechanism that classifies cells into meaningful priority categories (High Priority, Moderate Priority, and Baseline) rather than relying on unreliable absolute probability cutoffs.
5. **Build and Deploy an Interactive Web & Demonstration System**: Build an asynchronous FastAPI backend and a responsive React web interface powered by a Leaflet Canvas map, allowing users to inspect neighborhoods, scrub through historical monsoon replay dates, and test alert generation via a private demonstration Telegram bot.

### 1.6 Scope and Practical Limitations
To maintain academic honesty, we clearly define the boundaries of our mini-project:
- **Relative Susceptibility, Not Water Depth**: The model produces a *relative susceptibility ranking* that indicates which areas are more vulnerable compared to others on a given day. It does *not* predict the exact physical water level in centimeters or the speed of moving floodwaters.
- **Experimental Student Demonstration**: The system is an educational and exploratory prototype developed for an engineering mini-project. It is *not* a certified civic operational early warning system, and it must not be used for emergency public evacuations.
- **Rainfall Resolution**: Precipitation is sourced from gridded satellite-gauge products (CHIRPS at ~5.3 km resolution) and public weather APIs. While this captures city-scale differences, it cannot capture hyper-local cloudbursts spanning less than 1 kilometer.
- **Surface Terrain Only**: The model parameters are based on surface topography, land cover, and visible drain distances. The system has no real-time telemetry regarding underground pipe clogs, pump station failures, or temporary roadside debris blockages.

### 1.7 Organization of the Report
The remainder of this report is organized as follows:
- **Chapter 2 (Literature Review)** reviews relevant published academic papers on urban flood susceptibility, machine learning applications, and Bengaluru hydrology.
- **Chapter 3 (Problem Statement and Proposed Solution)** outlines our formal problem definition, user requirements, and proposed software architecture.
- **Chapter 4 (System Design and Architecture)** details the overall software design, backend API endpoints, frontend map engine, and cloud deployment setup.
- **Chapter 5 (Methodology)** explains the dataset preprocessing, spatial grid creation, the 18 input features, XGBoost training, and the daily ranking algorithm.
- **Chapter 6 (Implementation and Results)** presents the tools used, key code snippets, frontend screenshots, holdout validation results on the September 2022 monsoon, and the automated test suite.
- **Chapter 7 (Conclusion and Future Scope)** summarizes the project achievements, key engineering observations, and practical avenues for future improvement.

---

# CHAPTER 2 — LITERATURE REVIEW

### 2.1 Urban Flood Susceptibility Mapping Approaches
Urban flood susceptibility mapping has evolved significantly over the past two decades. In early civil engineering studies, flood mapping relied almost entirely on one-dimensional (1D) and two-dimensional (2D) numerical hydraulic models, such as HEC-RAS (Hydrologic Engineering Center's River Analysis System) and EPA SWMM (Storm Water Management Model). While these physical models are based on the conservation of mass and momentum, they require very detailed ground measurements. For example, engineers must know the exact cross-sections of every open channel, the underground pipe slopes, the surface roughness coefficients (Manning's *n*), and soil infiltration rates across every parcel of land.

In a comprehensive review, **Islam et al. (2025)** systematically evaluated modern urban flood susceptibility mapping techniques across remote sensing, machine learning, and physical models [1]. The authors observed that in rapidly developing urban centers, acquiring complete and updated drainage network data is often impossible due to rapid unauthorized construction, unmapped underground utilities, and municipal data fragmentation. Consequently, researchers have increasingly adopted geospatial multi-criteria evaluation and machine learning techniques. By combining digital elevation models (DEM), optical land-use classifications, and distance-to-water metrics, data-driven approaches can identify vulnerable natural hollows and water accumulation zones without requiring unfeasible underground civil telemetry [1].

### 2.2 Machine Learning in Flood-Related Studies
With the rapid increase in computing power and open remote-sensing datasets, machine learning has emerged as an effective tool for spatial susceptibility classification. A wide variety of algorithms have been explored in the literature, including Logistic Regression, Support Vector Machines (SVM), Random Forests, Artificial Neural Networks (ANN), and Gradient Boosted Decision Trees (such as XGBoost and LightGBM).

In a critical review of a decade of machine learning applications in flood mapping, **Pourzangbar et al. (2025)** evaluated the strengths and limitations of different algorithms [2]. Their study highlighted that decision-tree ensemble methods consistently outperform single decision trees and simple linear classifiers when applied to spatial flood data. This is because tree ensembles naturally model complex interaction effects—for instance, an area with a very gentle slope might only become dangerous when its surrounding soil is completely sealed by concrete and multi-day rainfall is high. 

Pourzangbar et al. also drew attention to a crucial practical challenge in flood modeling: **extreme class imbalance** [2]. In any historical dataset covering an entire city over several years, the vast majority of grid cells on most days do *not* experience flooding. True flood instances make up only a tiny fraction of one percent of the records. If an algorithm is trained naively on such data, it can achieve 99.9% accuracy by simply predicting "No Flood" every single time, which is useless in practice. The authors recommended using loss-function reweighting (such as `scale_pos_weight` in XGBoost) and evaluating models using Precision-Recall curves rather than misleading overall accuracy scores [2].

### 2.3 Rainfall and Hydrological Studies in Bengaluru
Understanding rainfall behavior is essential for any flood study in Bengaluru. Unlike coastal cities that face predictable monsoon storm tracks, Bengaluru’s monsoonal rains are heavily influenced by local convective thunderstorms that develop in the late afternoon and evening.

**Joseph et al. (2022)** conducted an extensive spatiotemporal reconstruction of urban rainfall across Bengaluru, analyzing rainfall variability dating back several decades [3]. Their research demonstrated that rainfall intensity in Bengaluru exhibits high spatial variation. The authors analyzed Areal Reduction Factors (ARF) across the BBMP territory and proved that rainfall correlation drops sharply once catchment sizes exceed 450 km². This explains a common phenomenon in Bengaluru: intense convective storms often dump 60 to 100 mm of rain over eastern areas like Bellandur and Mahadevapura, while western or northern zones receive less than 10 mm on the same evening. This finding strongly justified our project's decision to divide Bengaluru into multiple rainfall zones rather than applying a single citywide rainfall reading to every neighborhood.

At the ward level, **Pathak et al. (2025)** investigated flood damage mechanisms in the Koramangala–Challaghatta (KC) Valley, one of Bengaluru's most flood-prone regions [5]. Their study surveyed residents and businesses to understand how water enters buildings and identified critical topographical factors—especially ground elevation relative to nearby lakes and the high proportion of paved surfaces—as primary determinants of waterlogging. 

Similarly, **Mukhopadhyay and Das (2026)** developed a Composite Flood Risk Index focusing specifically on **Bellandur Ward (Ward 150)**, which was the epicenter of the catastrophic September 2022 floods [6]. Their analysis showed that Bellandur suffers from a structural drainage bottleneck: it sits at the receiving end of a very large upstream urban catchment where natural lake cascades have been broken by urban development. When heavy rainfall strikes, the incoming runoff rapidly exceeds the capacity of the remaining open stormwater drains, creating backflows into nearby residential and commercial layouts [6].

### 2.4 Technology-Enabled Flood Information Platforms
In addition to modeling algorithms, recent literature emphasizes the need for practical, accessible technology stacks to deliver geospatial flood information to users. **Al-Rawas et al. (2024)** reviewed emerging disaster mitigation technologies and stressed that a predictive model is only useful if its outputs can be visualized and understood by non-specialist stakeholders [4]. They pointed out that many academic models remain confined to complex desktop GIS software like ArcGIS or QGIS, which ordinary citizens or municipal field workers cannot easily run. The authors advocated for lightweight, cloud-hosted web dashboards and mobile-friendly communication tools that present hazard data clearly and promptly.

### 2.5 Comparative Analysis of Reviewed Literature
Table 1 summarizes the key research papers reviewed for this project, highlighting their focus area, core methodology, and how they influenced our work.

#### Table 1: Comparative Summary of Reviewed Literature
| Author & Year | Research Scope | Primary Methodology | Key Findings / Contribution | Influence on N²M Project |
| :--- | :--- | :--- | :--- | :--- |
| **Islam et al. (2025)** [1] | Global Urban Flood Susceptibility | Systematic Literature Review (Remote Sensing & ML) | Highlighted shift toward GIS terrain features (DEM, TWI, slope) due to lack of underground pipe data in growing cities. | Justified our selection of open terrain and land-cover features (SRTM, WorldCover, OSM). |
| **Pourzangbar et al. (2025)** [2] | Machine Learning Flood Mapping Review | Meta-Analysis of ML Algorithms & Imbalance | Proved that tree ensembles (XGBoost, Random Forest) handle non-linear terrain data best; highlighted class imbalance risks. | Guided our choice of XGBoost, positive loss weighting, and Precision-Recall metrics. |
| **Joseph et al. (2022)** [3] | Bengaluru Spatiotemporal Rainfall | Statistical Reconstruction & Areal Reduction Factors | Proved that rainfall across Bengaluru is highly variable; single-station weather readings fail for city-wide studies. | Inspired assigning each grid cell to localized satellite-gauge precipitation pixels. |
| **Al-Rawas et al. (2024)** [4] | Emerging Tech in Disaster Mitigation | Review of Cloud, AI, and IoT Systems | Emphasized that flood models need accessible web interfaces and automated messaging rather than complex GIS files. | Motivated our decoupled FastAPI backend, React web map, and Telegram demo bot. |
| **Pathak et al. (2025)** [5] | Bengaluru KC Valley Flood Analysis | Empirical Field Surveys & Spatial Analysis | Showed that low elevation relative to lakes and high concrete coverage are primary physical drivers of waterlogging. | Confirmed importance of HAND (Height Above Nearest Drainage) and imperviousness features. |
| **Mukhopadhyay & Das (2026)** [6] | Bellandur Ward Flood Risk Assessment | Multi-Criteria Spatial Indexing (MCDA) | Demonstrated that Bellandur Ward has high structural vulnerability due to broken lake chains and drainage bottlenecks. | Provided a verified local benchmark that helped us evaluate our September 2022 case study. |

### 2.6 Project Motivation and Identified Gaps
From our literature review, we identified several clear gaps that our undergraduate mini-project could address:
1. **Gap Between Complex Hydraulic Software and Lightweight Web Tools**: Most hydrological studies produce static PDF maps or heavy GIS shapefiles that require desktop software to view. There was a lack of simple, interactive web-based map interfaces designed to let everyday users explore neighborhood flood susceptibility.
2. **Failure of Single-Threshold Classifiers on Sparse Data**: Many machine learning papers apply a rigid 0.5 probability cutoff. On rare-event datasets where floods represent less than 0.1% of records, a 0.5 cutoff predicts zero events. There was a need for an intuitive, rank-based prioritization mechanism that highlights the top 5% or 10% highest-risk areas each day.
3. **Integration of Historical Monsoonal Replay**: Few student projects implement an interactive historical replay feature that allows users to step through a real historical flood sequence (such as the September 2022 monsoon) day by day to observe how changing antecedent rainfall affects spatial susceptibility scores.

These gaps directly motivated the design of our system architecture and experimental methodology.

---

# CHAPTER 3 — PROBLEM STATEMENT AND PROPOSED SOLUTION

### 3.1 Problem Statement
Urban flooding in Greater Bengaluru causes recurring property damage, traffic paralysis, and public safety hazards during the monsoon season. However, existing municipal alerts are issued at a broad, citywide scale, offering no neighborhood-level spatial distinction. Concurrently, traditional physical hydrodynamic modeling across the entire 711.59 km² urban territory is hindered by the absence of open, updated underground storm sewer telemetry.

Therefore, the core engineering problem addressed in this project is:  
*How to design, implement, and deploy an open-source, machine learning-driven geospatial platform that ingests public terrain and satellite-gauge precipitation data, discretizes Greater Bengaluru into uniform spatial cells, computes daily relative flood susceptibility rankings under severe class imbalance, and presents these insights through an accessible, interactive web interface and mobile demonstration bot.*

### 3.2 Existing Challenges
In developing this solution, our team had to overcome four major practical challenges:
1. **Severe Ground-Truth Label Scarcity**: Unlike temperature or atmospheric pressure, which are continuously recorded by weather stations, urban flooding occurs rarely in space and time. Across six major monsoonal storm events spanning several years, official municipal reports confirmed flooding in only 240 cell-days out of more than 1.76 million possible cell-day combinations (a prevalence of just 0.0136%).
2. **Spatial Rainfall Variability**: Convective thunderstorm cells in Bengaluru are highly localized. A uniform rainfall model would fail to capture why one quadrant of the city floods while another remains completely unaffected.
3. **High-Performance Map Rendering in Browsers**: Displaying 3,026 interactive polygons or dots on an interactive web map can cause severe browser sluggishness if standard DOM or SVG elements are used, since creating thousands of separate DOM nodes degrades rendering performance.
4. **Cloud Hosting on Free-Tier Resources**: As a student group with zero funding, the entire application stack—including the API server, machine learning data assets, and web dashboard—had to be engineered to run reliably within free-tier cloud limits (such as Render's 512 MB RAM ceiling).

### 3.3 Proposed Solution
To overcome these challenges, we engineered the **N²M Flood Prediction Model**, a decoupled geospatial web system structured into four coordinated layers:
1. **Geospatial Discretization and Data Pipeline**: The municipal area of Bengaluru (BBMP) is partitioned into a uniform Cartesian grid of **3,026 spatial cells** (~500 m × 500 m, 0.25 km² per cell). For every cell, 10 static terrain and built-environment metrics are precomputed from SRTM DEM, ESA WorldCover, and OpenStreetMap data.
2. **Multi-Pixel Rainfall Linkage**: Each cell is dynamically mapped to its nearest 0.05° Climate Hazards Center CHIRPS precipitation pixel (spanning 37 distinct pixels across the city), providing 8 daily and antecedent rainfall features.
3. **Imbalance-Aware XGBoost Model and Daily Ranking**: An XGBoost classifier is trained with positive loss weighting (`scale_pos_weight = 89.16`). Instead of using a fixed 0.5 threshold, the model ranks all 3,026 cells daily, categorizing them into **High Priority** (Top 150 cells / 5%), **Moderate Priority** (Ranks 151–300 / 5%), and **Baseline Risk** (Ranks 301–3,026 / 90%).
4. **Interactive Cloud Web Dashboard and Demonstration Bot**: A responsive React + Vite web application deployed on Vercel connects to an asynchronous FastAPI backend deployed on Render. An HTML5 Canvas layer on Leaflet renders all 3,026 cells at a smooth 60 frames per second, complete with cell attribute inspection drawers, 24-day historical replay scrubbing, and a private Telegram demonstration bot.

### 3.4 Functional Requirements
Table 2 outlines the key functional requirements (FR) implemented in the system.

#### Table 2: Functional Requirements Specification
| ID | Requirement Category | Description of Functional Capability |
| :--- | :--- | :--- |
| **FR-1** | Spatial Grid Generation | System must partition Greater Bengaluru into 3,026 uniform 500 m × 500 m cells covering all 198 BBMP administrative wards. |
| **FR-2** | Terrain Feature Ingestion | System must compute 10 static morphological features per cell from DEM, land cover, and vector road/water datasets. |
| **FR-3** | Rainfall Feature Linkage | System must link each cell to dynamic 0.05° CHIRPS precipitation grids to compute rolling 1-day, 2-day, 3-day, and 7-day rainfall sums. |
| **FR-4** | XGBoost Model Inference | System must load pre-trained XGBoost model weights and compute daily relative susceptibility scores across all 3,026 cells. |
| **FR-5** | Daily Dense Ranking | System must sort all cells daily and assign priority tiers: High (Top 150), Moderate (Ranks 151–300), and Baseline (Ranks 301–3,026). |
| **FR-6** | Interactive Web Map | Frontend must render all 3,026 cells on an OpenStreetMap canvas layer with color-coded risk markers and click-to-inspect popups. |
| **FR-7** | Historical Replay Engine | System must allow users to step through the 24-day September 2022 monsoon flood sequence, updating map colors dynamically. |
| **FR-8** | Demonstration Telegram Bot | Backend must provide a secure, whitelisted Telegram bot allowing authorized team members to request risk summaries via chat. |

### 3.5 Non-Functional Requirements
Table 3 outlines the non-functional performance and quality requirements (NFR) of the system.

#### Table 3: Non-Functional Requirements Specification
| ID | Requirement Dimension | Target Specification & Verification Criteria |
| :--- | :--- | :--- |
| **NFR-1** | Rendering Performance | Map visualization must maintain 60 FPS in standard modern web browsers during interactive panning, zooming, and replay scrubbing. |
| **NFR-2** | Backend API Latency | Spatial risk queries (`/api/risk`) must return complete 3,026-cell JSON payloads in under 500 milliseconds under normal network conditions. |
| **NFR-3** | Memory Footprint | Backend memory consumption must remain below 100 MB resident RAM to comfortably operate on free-tier hosting (512 MB limit). |
| **NFR-4** | Token & Credential Security | Secrets such as `TELEGRAM_BOT_TOKEN` must reside exclusively in server environment variables and never be exposed in frontend bundles or Git. |
| **NFR-5** | Code Quality & Testing | The backend test suite must achieve 100% pass rate across core endpoints, data schemas, and security authorization checks. |
| **NFR-6** | Cross-Browser Usability | The web interface must function correctly across major modern desktop and mobile browsers (Chrome, Firefox, Safari, Edge). |

### 3.6 Scope and Operational Boundaries
To ensure that users, evaluators, and the public do not misunderstand the purpose of this project, the following operational boundaries are strictly enforced:
- **Academic and Educational Purpose**: The system is designed as an academic mini-project to demonstrate the application of machine learning and geospatial data science to urban hydrology. It is not an operational municipal emergency warning system.
- **No Real-Time Flood Guarantees**: Predictions represent *relative susceptibility rankings* based on terrain and estimated rainfall. The system does not guarantee that flooding will or will not occur at an exact street address or specific minute.
- **Restricted Telegram Bot**: The Telegram bot is restricted to whitelisted student group chat IDs to prevent unauthorized use or public misinterpretation of experimental demonstration alerts.
"""
