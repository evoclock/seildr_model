#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scenario_simulator.py — Streamlit interactive simulator

Author: Julen Gamboa
Date: 06/2025

Description:
---------------------------------------
Interactive web-based simulator for the SEILDR stochastic model of Pacheco's Disease.
Allows real-time exploration of parameter space with visual output and CSV export.

How to launch:
---------------------------------------
From project root, activate virtual environment and run:

    streamlit run src/seildr_sim/scenario_simulator.py

or if running from inside package root:

    streamlit run seildr_sim/scenario_simulator.py

Notes:
---------------------------------------
- Automatically detects CPU cores (max 10 for safety).
- All parameter settings controlled via sidebar sliders.
- Results can be downloaded for further offline analysis.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
from seildr_sim.core_model import run_simulation
import multiprocessing

# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------

st.title("Pacheco's Disease Management Simulator")

st.sidebar.header("Simulation Parameters")

initial_infectious = st.sidebar.slider("Initial Infectious Count", 0, 20, 6, 1)
initial_latent = st.sidebar.slider("Initial Latent Count", 0, 80, 30, 1)
beta_within = st.sidebar.slider("Within Aviary Transmission", 0.0, 0.5, 0.1, 0.01)
beta_cross = st.sidebar.slider("Cross Aviary Transmission", 0.0, 0.05, 0.02, 0.001)
mortality = st.sidebar.slider("Mortality Rate", 0.0, 1.0, 0.5, 0.05)
reactivation_p = st.sidebar.slider("Daily Reactivation", 0.0, 0.01, 1/3650, 0.0001)
repeats = st.sidebar.slider("Number of Repeats", 10, 1000, 200, 10)
sim_days = st.sidebar.slider("Simulation Duration (days)", 365, 365*5, 1095, 365)

# Limit cores explicitly to your machine capacity
n_cores = min(10, multiprocessing.cpu_count())
st.sidebar.write(f"Using {n_cores} CPU cores")

st.write("Running simulation...")

results = run_simulation(
    initial_infectious=initial_infectious,
    initial_latent=initial_latent,
    beta_within=beta_within,
    beta_cross=beta_cross,
    mortality_rate=mortality,
    reactivation_daily_p=reactivation_p,
    repeats=repeats,
    days=sim_days,
    n_cores=n_cores
)

# ---------------------------------------------------
# Plotting
# ---------------------------------------------------

cumulative_results = np.cumsum(results, axis=1)
mean_cum = np.mean(cumulative_results, axis=0)
lower = np.percentile(cumulative_results, 2.5, axis=0)
upper = np.percentile(cumulative_results, 97.5, axis=0)

plt.figure(figsize=(10, 6))
plt.fill_between(np.arange(sim_days), lower, upper, color='lightblue', alpha=0.5, label="95% interval")
plt.plot(mean_cum, label="Mean Cumulative Deaths", color='blue')
plt.xlabel("Days")
plt.ylabel("Cumulative Deaths")
plt.title("Pacheco's Disease Scenario Simulation")
plt.legend()
plt.grid()
st.pyplot(plt)

# Export CSV option
export_df = pd.DataFrame(cumulative_results.T)
export_df.index.name = "Day"
buffer = io.BytesIO()
export_df.to_csv(buffer)
buffer.seek(0)

st.download_button(
    label="Download Results CSV",
    data=buffer,
    file_name="simulation_results.csv",
    mime="text/csv"
)