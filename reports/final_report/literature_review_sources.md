# N²M Flood Prediction Model — Scientific Literature Review Sources & Verification

This document compiles the formal bibliographic records, verified abstracts, methodological summaries, and comparative relevance notes for the peer-reviewed papers analyzed in Chapter 2 of the final academic project report.

---

## 1. Core Literature Sources

### Paper 1: Systematic Review of Urban Flood Susceptibility Mapping
- **Full Citation**: Islam, T., Zeleke, E. B., Afroz, M., & Melesse, A. M. (2025). A Systematic Review of Urban Flood Susceptibility Mapping: Remote Sensing, Machine Learning, and Other Modeling Approaches. *Remote Sensing*, 17(3), 524.
- **DOI**: [10.3390/rs17030524](https://doi.org/10.3390/rs17030524)
- **Publication Date**: February 2025
- **Journal**: *Remote Sensing* (MDPI, Open Access)
- **Core Themes**:
  - Global trends in urban flood susceptibility mapping (UFSM) driven by urbanization and climate change.
  - Dominance of remote sensing datasets: digital elevation models (DEM), Sentinel/Landsat multispectral imagery, and radar backscatter.
  - Frequency of conditioning parameters: elevation, slope, TWI, distance to rivers/roads, LULC imperviousness, and rainfall indices.
  - Methodological shift from traditional hydraulic 1D/2D models (HEC-RAS, SWMM) to machine learning and GIS-based data-driven models.
- **Relevance to N²M**:
  - Grounds the 18 conditioning features used in the N²M framework (SRTM DEM, slope, TWI, HAND, impervious fraction, lake/drain distances).
  - Validates why ML susceptibility mapping serves as a computationally viable alternative to full hydraulic modeling in data-sparse urban basins.
- **Key Limitations Highlighted by Authors**:
  - Data scarcity in developing world metropolises; coarse satellite rainfall resolution failing to capture micro-urban convective storms.

---

### Paper 2: Analysis of Machine Learning Utilization in Flood Susceptibility Mapping
- **Full Citation**: Pourzangbar, A., Oberle, P., Kron, A., & Franca, M. J. (2025). Analysis of the Utilization of Machine Learning to Map Flood Susceptibility. *Journal of Flood Risk Management*, 18, e70042.
- **DOI**: [10.1111/jfr3.70042](https://doi.org/10.1111/jfr3.70042)
- **Publication Date**: 2025
- **Journal**: *Journal of Flood Risk Management* (Wiley)
- **Core Themes**:
  - Critical review synthesizing a decade (2013–2023) of ML applications in flood susceptibility mapping.
  - Investigation of trial-and-error practices, hyperparameter tuning, and class imbalance handling.
  - Comparative performance of tree-based ensembles (Random Forest, XGBoost) versus SVM, Multi-Layer Perceptrons, and deep learning.
  - Need for reproducible workflows, feature collinearity audits, and explicit model explainability.
- **Relevance to N²M**:
  - Confirms XGBoost's superior handling of non-linear hydrological interactions and extreme class imbalance.
  - Directly justifies N²M's `scale_pos_weight = 89.16` parameterization and out-of-sample holdout validation protocol.
- **Key Distinctions / Limitations**:
  - Notes that uncalibrated model probabilities often cluster near zero when class imbalance is severe; supports N²M's rank-based thresholding approach.

---

### Paper 3: Spatiotemporal Reconstruction of Urban Rainfall in Bengaluru
- **Full Citation**: Joseph, R., Mujumdar, P. P., & Das Bhowmik, R. (2022). Reconstruction of Urban Rainfall Measurements to Estimate the Spatiotemporal Variability of Extreme Rainfall. *Water*, 14(23), 3900.
- **DOI**: [10.3390/w14233900](https://doi.org/10.3390/w14233900)
- **Publication Date**: November 2022
- **Journal**: *Water* (MDPI, Open Access)
- **Core Themes**:
  - Focuses explicitly on the hydrometeorology of Bengaluru, India.
  - Historical rainfall monitoring in Bengaluru was historically limited to 2 long-term IMD ground stations (Bangalore City and HAL Airport), while KSNDMC telemetric rain gauges were only deployed in recent years.
  - Employs Random Forest regression to reconstruct sub-daily historical precipitation series across the urban area dating back to 1969.
  - Evaluates Intensity–Duration–Frequency (IDF) curves and Areal Reduction Factors (ARF).
- **Relevance to N²M**:
  - Provides critical academic evidence for Bengaluru's extreme spatial rainfall variability: ARF drops significantly above 450 km², explaining why northern wards remain dry while eastern wards (Bellandur) experience inundation.
  - Directly supports N²M's multi-pixel dynamic rainfall framework (allocating cells to 37 distinct CHIRPS precipitation pixels across the city).

---

### Paper 4: Critical Review of Emerging Technologies for Flash Flood Prediction
- **Full Citation**: Al-Rawas, G., Nikoo, M. R., Al-Wardy, M., & Etri, T. (2024). A Critical Review of Emerging Technologies for Flash Flood Prediction: Examining Artificial Intelligence, Machine Learning, Internet of Things, Cloud Computing, and Robotics Techniques. *Water*, 16(14), 2069.
- **DOI**: [10.3390/w16142069](https://doi.org/10.3390/w16142069)
- **Publication Date**: July 2024
- **Journal**: *Water* (MDPI, Open Access)
- **Core Themes**:
  - Systematic review of literature (2010–2023) across AI/ML (64% of studies), IoT (19%), Cloud Computing (6%), and Robotics (2%).
  - Demonstrates that modern disaster mitigation requires integrated cyber-physical workflows combining predictive modeling with cloud-based alert distribution.
  - Examines common points of failure: network disconnections in cloud/IoT nodes, sensor drift, and lack of accessible visualization interfaces for civic stakeholders.
- **Relevance to N²M**:
  - Informs N²M's complete end-to-end architecture: coupling ML inference with modern cloud hosting (Render/Vercel) and interactive web cartography.
  - Validates the role of automated messaging APIs (Telegram demonstration bot) for controlled alert delivery.

---

## 2. Supporting Literature Sources

### Paper 5: Socio-Economic Variables in Urban Flood Damage Assessments (Bengaluru)
- **Full Citation**: Pathak, A. A., Mathad, A. R., & Gagnon, A. S. (2025). Integrating Socio-Economic Variables in Urban Flood Damage Assessments: A Case Study of Bengaluru, India. *Natural Hazards*, 121, 1007/s11069-024-07019-9.
- **DOI**: [10.1007/s11069-024-07019-9](https://doi.org/10.1007/s11069-024-07019-9)
- **Publication Date**: Published online 2024 / Volume in 2025
- **Journal**: *Natural Hazards* (Springer)
- **Core Themes**:
  - Empirical case study in Bengaluru's flood-prone **Koramangala–Challaghatta (KC) Valley**.
  - Collects household and commercial property surveys to formulate empirical stage-damage curves.
  - Uses Random Forest to identify primary loss drivers: water depth, asset value, structural material, and property type.
  - Clarifies that high-value commercial entities often exhibit adaptive flood mitigation capacity (sumps, barriers), whereas residential informal sectors face severe unmitigated loss.
- **Relevance & Boundary Distinction for N²M**:
  - Establishes vital terminological clarity: **Susceptibility** (physical likelihood of ponding based on terrain/rain) vs. **Vulnerability** (susceptibility to harm) vs. **Exposure** (assets in hazard path) vs. **Damage** (financial/structural loss).
  - Clarifies that N²M focuses strictly on physical *flood susceptibility*, not socioeconomic damage modeling.

---

### Paper 6: Composite Flood Risk Index Assessment for Bellandur Ward, Bengaluru
- **Full Citation**: Mukhopadhyay, P., & Das, B. K. (2026). Composite Flood Risk Index Assessment and Operationalization for Bellandur Ward, Bengaluru. *Engineering, Technology & Applied Science Research*, 16(4), 37667–37672.
- **DOI**: [10.48084/etasr.18047](https://doi.org/10.48084/etasr.18047)
- **Publication Date**: August 2026
- **Journal**: *Engineering, Technology & Applied Science Research* (ETASR)
- **Core Themes**:
  - Formulates a Composite Flood Risk Index (CFRI) for **Bellandur Ward (Ward 150)**, the epicenter of Bengaluru's 2022 flood crisis.
  - Combines Normalized Static Flood Risk (NSFR, 24 attributes via MCDA) with a Real-Time Flood Alert Index (RTFAI) modified by an urban drainage amplification factor ($\alpha = 1.2$).
  - Evaluates Bellandur's NSFR at 0.89 (critically high) and demonstrates CFRI exceeding 1.0 during September 2022 peak rainfall.
- **Relevance & Comparison with N²M**:
  - Focuses on the exact geographic epicenter analyzed in N²M's validation study (Cell #722 is located in Ward 150 Bellandur).
  - Provides a critical benchmark comparing an indicator-based Multi-Criteria Decision Analysis (MCDA) framework with N²M's data-driven gradient-boosted decision tree (XGBoost) approach.

---

### Paper 7: Early Warning Systems for Urban Flood Resilience
- **Full Citation**: Pham Ngoc Thinh. (2025). Early Warning Systems for Urban Flood Resilience. *Reviews in Agricultural Science*, 13, 61–74.
- **DOI**: [10.7831/ras.13.4_61](https://doi.org/10.7831/ras.13.4_61)
- **Publication Date**: November 2025
- **Journal**: *Reviews in Agricultural Science* (J-STAGE)
- **Core Themes**:
  - Systematic review of Early Warning Systems (EWS) as non-structural urban resilience measures under the PRISMA methodology.
  - Analysis of sensor networks, hydrodynamic predictive tools, and multi-tier alert communication mechanisms.
  - Emphasizes the frequent disconnect between technical model outputs and stakeholder comprehension in low-resource environments.
- **Relevance to N²M**:
  - Reinforces N²M's emphasis on clean, cartographic visualization (Leaflet Canvas, color-coded priority tiers) and human-readable demonstration bulletins over raw probabilities.

---

### Paper 8 (Optional): Computer Vision and IoT Sensors in Flood Monitoring
- **Full Citation**: Arshad, B., Ogie, R., Barthelemy, J., Pradhan, B., Verstaevel, N., & Perez, P. (2019). Computer Vision and IoT-Based Sensors in Flood Monitoring and Mapping: A Systematic Review. *Sensors*, 19(22), 5012.
- **DOI**: [10.3390/s19225012](https://doi.org/10.3390/s19225012)
- **Publication Date**: November 2019
- **Journal**: *Sensors* (MDPI, Open Access)
- **Core Themes**:
  - Reviews wireless sensor networks, CCTV cameras, drones/UAVs, and computer vision algorithms for dynamic water depth measurement and validation.
- **Relevance to N²M**:
  - Informs future work regarding ground-truth verification through crowdsourced or CCTV imagery to address N²M's sparse label limitation.

---

## 3. Comparative Literature Synthesis Matrix

| Study | Authors & Year | Region | Core Methodology | Key Findings | Relevance to N²M | Critical Distinction / Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UFSM Systematic Review** | Islam et al. (2025) [1] | Global Urban Metropolises | PRISMA Systematic Review of RS & ML literature | DEM indices, TWI, and LULC are the top conditioning features; ML outpaces traditional 1D/2D models in computation speed. | Directly supports N²M's 18-feature topographic & built environment design. | Broader survey; does not implement an operational spatial pipeline for a specific Indian city. |
| **ML Utilization in FSM** | Pourzangbar et al. (2025) [2] | Global Catchments (2013–2023) | Comparative critical review of ML architectures | Tree ensembles (RF, XGBoost) offer optimal balance of accuracy, collinearity handling, and interpretability; class imbalance is often mishandled. | Justifies XGBoost selection and `scale_pos_weight` tuning in N²M. | Emphasizes probabilistic modeling rather than rank-based spatial thresholding. |
| **Urban Rain Reconstruction** | Joseph et al. (2022) [3] | Bengaluru, Karnataka, India | Random Forest regression for sub-daily rain reconstruction | Demonstrates significant intra-city spatial rainfall variability; ARF drops sharply above 450 km². | Empirically confirms that Bengaluru cannot be modeled with a single rain gauge; validates N²M's 37 CHIRPS pixels. | Focused on historical rainfall series reconstruction rather than flood inundation or susceptibility mapping. |
| **Emerging Flood Tech** | Al-Rawas et al. (2024) [4] | Global (Flash Flood Basins) | Critical review of AI, IoT, Cloud, and Robotics | AI/ML represents 64% of innovations; cloud-hosted GIS platforms enable real-time dissemination. | Validates N²M's decoupled cloud deployment (Vercel + Render) and messaging bot integration. | Highlights that cloud systems often lack local ground-truth calibration in developing countries. |
| **Socioeconomic Damage** | Pathak et al. (2025) [5] | KC Valley, Bengaluru, India | Household surveys + Random Forest regression | Flood depth dictates losses; residential damage scales with asset value, while commercial entities deploy adaptive defenses. | Provides deep local context on the Koramangala–Challaghatta Valley; clarifies terminology (susceptibility vs. damage). | Focuses on socioeconomic loss and financial damage functions, whereas N²M models physical terrain susceptibility. |
| **Composite Flood Risk** | Mukhopadhyay & Das (2026) [6] | Bellandur Ward (Ward 150), Bengaluru | Multi-Criteria Decision Analysis (MCDA) + Static/Real-time index | Evaluates Bellandur NSFR at 0.89; CFRI exceeded 1.0 during September 2022 peak rainfall. | Validates N²M's identification of Ward 150 (Cell 722) as the top citywide susceptibility hotspot. | Index-based weighted scoring (MCDA) based on 24 manual criteria; N²M uses data-driven gradient boosted trees. |
| **Urban Flood EWS** | Pham Ngoc Thinh (2025) [7] | Developing World Urban Centers | PRISMA review of EWS non-structural measures | Identifies institutional communication gaps as the primary cause of EWS failure; urges clear risk tiers over raw metrics. | Informs N²M's rank-based alert tiers (High/Moderate/None) and Telegram bulletin design. | Qualitative review of EWS governance and resilience frameworks. |
| **IoT & Vision Monitoring** | Arshad et al. (2019) [8] | Global Sensor Deployments | Systematic review of IoT and computer vision | Wireless sensor networks and camera feeds can validate flood presence in real-time. | Informs future data collection pipelines to address N²M's ground-truth label sparsity. | Physical sensor hardware and image processing review; outside N²M's software scope. |

---

## 4. Synthesized Research Gap & Project Motivation
1. **The Gap in Academic Literature**:
   - Advanced hydrodynamic models (e.g. 2D MIKE FLOOD, SWMM) are computationally prohibitive for full-city continuous daily assessment across Bengaluru (711 km²).
   - Indicator-based index frameworks (e.g. MCDA, AHP) rely on subjective weight assignments that cannot learn complex non-linear interactions.
   - Machine learning flood studies often treat flood prediction as an abstract classification exercise, reporting high ROC-AUC on artificially balanced datasets while failing to address real-world class imbalance (1 : 7,350), spatial label leakage, or actionable civic delivery.
2. **Defensible Project Contribution**:
   - The **N²M Flood Prediction Model** addresses this gap by implementing and demonstrating a complete, transparent, decoupled geospatial research system. It pairs an explainable gradient-boosted decision tree (XGBoost) with a uniform 3,026-cell spatial skeleton, enforces strict out-of-sample holdout validation on the historic September 2022 monsoon event, and translates uncalibrated outputs into daily operational rank tiers presented via a high-performance interactive cartographic web interface and private Telegram messaging demonstration.
