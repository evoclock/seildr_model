# Avian Herpesvirus/Pacheco’s Disease Simulation and Management Model

Author: Julen Gamboa

Date: 10/06/2025

---

##  Biological Context

This pipeline models long-term epidemiological dynamics of Pacheco’s disease in a closed multi-aviary population of macaws and African grey parrots. The model supports management decision-making by evaluating:

- Biosecurity interventions
- Chronic carrier dynamics
- Cross-aviary indirect transmission
- Latency reactivation risk
- Strain-specific mortality rates

It accounts for both **acute outbreaks** (high-mortality phases) and **chronic latent carriage** (lifelong infected survivors), consistent with known biological behavior of avian herpesviruses (PsHV-1 complex).

---

##  Model Overview

The model implements a stochastic **SEILDR structure**, where:

- **S**: Susceptible
- **E**: Exposed (incubating, not yet infectious)
- **I**: Infectious (actively shedding virus)
- **L**: Latent (chronically infected carriers)
- **D**: Dead
- **R**: Reactivation (latent carriers may occasionally revert to infectious)

Transmission occurs via:

- **Within-aviary transmission** (`beta_within`): physical contact, shared perches/feeders.
- **Cross-aviary transmission** (`beta_cross`): air circulation, fomite transmission across adjacent enclosures, potential cross-contamination introduced by keepers.

Key biological parameters include:

- Variable mortality rate depending on viral strain.
- Chronic latency with rare but ongoing reactivation.
- Indirect and direct transmission paths.
- Initial seeding of both actively infectious and latent carriers.

The model runs on daily time steps and uses explicit event-based transitions simulated via stochastic binomial draws.

---

##  Directory Layout

```text
project_root/
│
├── pyproject.toml              # Build and package configuration (PEP 621 / setuptools)
├── README.md                   # Full documentation file (this file)
├── requirements.txt            # Dependency specification (for classic pip installs)
│
├── src/                        # Project source code lives entirely under src layout
│   └── seildr_sim/             # Main simulation package
│       ├── __init__.py         # Package initializer
│       ├── path_resolver.py    # Resolves scenario/data paths internally
│       ├── core_model.py       # Stochastic SEILDR model engine
│       ├── simulate_runner.py  # Interactive + CLI simulator
│       ├── batch_scenario_runner.py  # Full factorial batch runner from CSV grid
│       ├── aggregate_results.py      # Aggregates batch outputs into summary CSV
│       ├── analyze_results.py        # Interactive replicate visualizer
│       ├── multi_panel_analytics.py  # Generates heatmaps, thresholds, stability maps
│       ├── scenario_simulator.py     # Streamlit interactive frontend
│       ├── generate_scenarios_csv.py # Factory script to generate scenario grids
│       ├── bayesian_model.py         # Experimental Bayesian PyMC5 model scaffold
│       └── inference_runner.py       # Experimental PyMC5 posterior runner
│
│   └── scenarios/             # Canonical parameter grid (input to batch runner)
│       └── scenarios.csv
│
├── results/                    # Output directory (generated after runs)
│   ├── *.npy                   # Raw individual simulation replicate outputs
│   └── summaries/              # Aggregated batch analysis results
│       ├── aggregate_summary.csv  # Full numeric summary
│       ├── heatmaps/           # Heatmaps for mortality vs latent/infectious seeding
│       ├── thresholds/         # Extinction vs outbreak zone classification
│       └── stability/          # Variance-based stability/sensitivity maps
│
├── logs/                       # Logging outputs for CLI runs
└── literature/                 # (Optional) Supporting scientific background & references
```

---


##  Scripts Overview Table

| Script                      | Role                          | Notes                                          |
| --------------------------- | ----------------------------- | ---------------------------------------------- |
| `core_model.py`             | Main stochastic SEILDR engine | Parallelized, called internally by all runners |
| `simulate_runner.py`        | Interactive + CLI runner      | Interactive when no arguments provided         |
| `batch_scenario_runner.py`  | Batch grid runner             | Reads scenarios from `scenarios.csv`           |
| `generate_scenarios_csv.py` | Scenario grid generator       | Auto-generates full parameter sweeps           |
| `aggregate_results.py`      | Result aggregator             | Collapses raw outputs into summary CSV         |
| `multi_panel_analytics.py`  | Full analytics & plotting     | Heatmaps, stability maps, extinction maps      |
| `analyze_results.py`        | Per-file visual QC            | Useful for inspecting specific runs            |
| `scenario_simulator.py`     | Streamlit interactive app     | Live scenario simulation                       |
| `bayesian_model.py`         | Bayesian model scaffold       | PyMC5 model structure                          |
| `inference_runner.py`       | Bayesian inference runner     | Experimental posterior inference               |


---

##  Scenario Grid (`scenarios.csv`)

This file fully controls the batch factorial sweeps.

| Column | Description |
|--------|-------------|
| scenario | Scenario name (`do_nothing`, `isolation_only`, `isolation_biosecurity`) |
| initial_infectious | Number of initial infectious birds |
| initial_latent | Number of initial latent carriers |
| mortality | Mortality rate (strain dependent) |
| reactivation | Daily reactivation probability |
| repeats | Number of stochastic replicates |
| days | Simulation duration (days) |
| cores | Cores used per scenario run |

---

##  Plot Types & Interpretation

### 1. Heatmaps
- Mortality vs initial latent seeding (`heatmaps/latent/`) 
- Mortality vs initial infectious seeding (`heatmaps/infectious/`)

Purpose: 
- Map outbreak severity across key parameter combinations.
- Show how mortality interacts with seeding to drive cumulative deaths.
- Allow management comparison of biosecurity scenarios.
- Reveal nonlinear tipping-points in outbreak dynamics.

### 2. Rankings
- Top 10 best parameter combinations minimizing deaths.

Purpose: 
- Management target identification.
- Highlight parameter combinations producing lowest death burdens.
- Identify optimal zones for management focus.

### 3. Threshold maps
Classify parameter regions into:
  - Extinction zones (outbreak dies out)
  - Outbreak zones (persistent epidemic risk)

- Classify whether extinction or outbreak occurs at each parameter combination.
- Binary extinction defined by configurable death threshold.

### 4. Stability maps
- Heatmaps of standard deviation across replicates.
- High variance indicates sensitive outbreak thresholds and unstable equilibrium zones.

Purpose: 
- locate high-variance regions where management outcome is highly sensitive to stochastic noise.

### 5. Time series (optional)
- Individual cumulative death curves per scenario replicate.

---

##  Script Descriptions

### `core_model.py`

- Implements full stochastic SEILDR model.
- Parallelized internally across replicates.
- Fully parameterized with:
  - Initial infectious count
  - Initial latent carriers
  - Transmission rates (`beta_within`, `beta_cross`)
  - Mortality rate
  - Reactivation probability
  - Duration of simulation
  - Number of replicates

### `simulate_runner.py`

- CLI runner for executing single scenarios interactively or via command line.
- Allows rapid exploratory testing of parameter combinations.

Example usage:
```
python simulate_runner.py 
   --scenario isolation_only 
   --initial_infectious 6 
   --initial_latent 30 
   --mortality 0.5 
   --repeats 1000 
   --days 2000 
   --cores 10
 ```  


### `batch_scenario_runner.py`

- Reads full scenario grid from `scenarios.csv`.
- Loops across:
  - Scenario type
  - Mortality rate
  - Seeding of infectious and latent birds
- Fully parallelized internally; serial across scenarios (safe parallelism).

### `aggregate_results.py`

- Aggregates all raw simulation `.npy` files into one `aggregate_summary.csv`.
- Computes:
  - Mean cumulative deaths
  - Confidence intervals (2.5%, 97.5%)
  - Standard deviation of final deaths (used for stability maps)

### `multi_panel_analytics.py`

- Full multi-layer analysis module.
- Generates:
  - **Latent heatmaps:** how initial latent load interacts with mortality.
  - **Infectious heatmaps:** how infectious seeding interacts with mortality.
  - **Rankings:** top parameter combinations minimizing deaths.
  - **Threshold maps:** classifies extinction vs outbreak regions.
  - **Stability maps:** variance zones indicating sensitivity to stochastic effects.

### `analyze_results.py` (optional)

- Per-scenario time-series plots.
- Useful for checking individual stochastic replicates.

---

##  Recommended Execution Order
### 1. Generate parameter grid (only once)
```
python -m seildr_sim.generate_scenarios_csv
```

### 2. Run full batch simulations
```
python -m seildr_sim.batch_scenario_runner
```

### 3. Aggregate raw results
```
python -m seildr_sim.aggregate_results
```

### 4. Perform analytics & generate plots
```
python -m seildr_sim.multi_panel_analytics
```

### 5. Optional — Visual inspection of individual replicates
```
python -m seildr_sim.analyze_results
```

### 6. Optional — Streamlit GUI for interactive exploration
```
streamlit run src/seildr_sim/scenario_simulator.py
```

### Notes on Bayesian Module
The `bayesian_model.py` and `inference_runner.py` modules are included as experimental scaffolds for future inference, but not validated in full production runs.


## Installation & Setup
### 1. Create virtual environment (recommended name):
```
python3 -m venv .seildr_venv
source .seildr_venv/bin/activate
```

### 2. Install dependencies:
```
pip install -r requirements.txt
```

### 3. Install package in editable mode:
```
pip install -e .
```

For scientific use, please cite:

Gamboa J. SEILDR: Stochastic modeling of Pacheco's Disease transmission and management in closed parrot populations. 2025. Github Repository: https://github.com/evoclock/seildr_model

##  Full Example Report

A complete demonstration of the model output is available here:

👉 [Download SEILDR Simulation Report (PDF)](./docs/seildr_comparative_report.pdf)
>>>>>>> 3f85222 (Initial clean release of SEILDR model with reproducible pipeline, Quarto reports, and documentation.)
