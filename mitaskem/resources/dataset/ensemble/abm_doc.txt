[![medRxiv](https://img.shields.io/badge/medRxiv-2021.10.19-blue)](https://www.medrxiv.org/content/10.1101/2021.10.19.21265221v1) [![mendeley](https://img.shields.io/badge/Mendeley-Add%20to%20Library-critical.svg)](https://www.mendeley.com/import/?url=https://www.medrxiv.org/content/10.1101/2021.10.19.21265221v1) [![contributions-welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/Shakeri-Lab/COVID-SEIR/pulls) [![researchgate](https://img.shields.io/badge/ResearchGate-HHAR_net-blue.svg?style=flat)](https://www.researchgate.net/publication/355470285_Wastewater-Based_Epidemiological_Modeling_for_Continuous_Surveillance_of_COVID-19_Outbreak)



COVID-19 Wastewater Surveillance: An Epidemiological Model :mask:
=============================================================

A Simple SEIR
=============================================================

Using wastewater surveillance as a continuous pooled sampling technique has been in place in many countries since the early stages of the outbreak of COVID-19. Since the beginning of the outbreak, many research works have emerged, studying different aspects of *viral SARS-CoV-2 DNA concentrations* (viral load) in wastewater and its potential as an early warning method. However, one of the questions that has remained unanswered is the quantitative relation between viral load and clinical indicators such as daily cases, deaths, and hospitalizations. Few studies have tried to couple viral load data with an epidemiological model to relate the number of infections in the community to the viral burden. We propose a **stochastic wastewater-based SEIR model** to showcase the importance of viral load in the early detection and prediction of an outbreak in a community. We built three models based on whether or not they use the case count and viral load data and compared their *simulations* and *forecasting* quality.

We consider a stochastic wastewater-based epidemiological model with four compartments (hidden states) of susceptible (S), exposed (E), infectious (I), and recovered/removed (R).


<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/SEIR_schematic_col.PNG" width="500"/>

--------------------
Model Specifications
--------------------

We define the **force of infection** as below:

<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/foi-SEIR.PNG" width="250"/>

**&iota;** is the imported infection, **&alpha;** is the mixing parameter, and ***w*** is the Gamma white noise. 

The rest of the parameters are summarized in table below:

<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/all-params.PNG" width="700"/>

We used **iterated filtering** in "*pomp*" package in **R** to estimate the parameters for the three models.

**Models to compare:**
  * SEIR-VY: Model that uses both *viral load* data and *case count* data
  * SEIR-V: Model that uses only *viral load* data
  * SEIR-Y: Model that uses only *case count* data

Maximum Likelihood Estimation (MLE) parameters of the three models:

<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/est-params.PNG" width="450"/>

-------
Results
-------

**Estimated Basic Reproduction Number R0**

* SEIR-VY model: R0=1.46
* SEIR-V model:  R0=1.08
* SEIR-Y model:  R0=1.92

**Simulation Comparison**

<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/sims-Y-noT.png" width="500"/>

<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/sims-V-noT.png" width="500"/>

**Forecasting Comparison**

In addition to the three models we also fitted an Autoregressive Integrated Moving Average (ARIMA) model.

<img src="https://github.com/Shakeri-Lab/COVID-SEIR/blob/main/figs/comp-forecast-zoom.png" width="500"/>

----------
Conclusion
----------

In this study, we implemented a SEIR model for three cases of using merely case count data, viral load data, and both. We allowed for stochasticity in the transmission rates and extra-demographic stochasticity accounting for the unforeseen events. We fitted our models using a simulation-based inference called Iterated Filtering. We compared the models from three different aspects, parameter estimation, simulation, and prediction. Our results suggest that the viral load data is an informative data source for monitoring the spread of COVID-19 cases on a community level. The viral load has enough information, which enables it to approximate the number of infected cases when employed with a proper epidemiological model. Additionally, viral load data is more consistent and less uncertain, making it a critical part of COVID-19 surveillance.

---
*For more detailed information of our modeling and references please refer to our paper*

---
Cite us:
---
```
@article {Fazli2021.10.19.21265221,
	author = {Fazli, Mehrdad and Sklar, Samuel and Porter, Michael D and French, Brent A and Shakeri, Heman},
	title = {Wastewater-Based Epidemiological Modeling for Continuous Surveillance of COVID-19 Outbreak},
	elocation-id = {2021.10.19.21265221},
	year = {2021},
	doi = {10.1101/2021.10.19.21265221},
	publisher = {Cold Spring Harbor Laboratory Press},
	URL = {https://www.medrxiv.org/content/early/2021/10/20/2021.10.19.21265221},
	eprint = {https://www.medrxiv.org/content/early/2021/10/20/2021.10.19.21265221.full.pdf},
	journal = {medRxiv}
}
```
