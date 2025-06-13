#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_scenario_runner.py — Fully package-aligned, parallel batch runner
"""

import pandas as pd
import numpy as np
import os
from seildr_sim.core_model import run_simulation
from seildr_sim.path_resolver import resolve_scenarios_path
from tqdm import tqdm

# ---------------------------------------
# Management scenarios mapping
# ---------------------------------------
SCENARIOS = {
    "do_nothing": {"beta_within": 0.5, "beta_cross": 0.02},
    "isolation_only": {"beta_within": 0.2, "beta_cross": 0.01},
    "isolation_biosecurity": {"beta_within": 0.05, "beta_cross": 0.002}
}

# ---------------------------------------
# Load scenario grid
# ---------------------------------------
scenario_path = resolve_scenarios_path()
if not os.path.exists(scenario_path):
    raise FileNotFoundError(f"Cannot find scenarios.csv at: {scenario_path}")

df = pd.read_csv(scenario_path)

# ---------------------------------------
# Ensure output directory exists
# ---------------------------------------
os.makedirs("results", exist_ok=True)

# ---------------------------------------
# Batch loop with progress bar
# ---------------------------------------
for idx, row in tqdm(df.iterrows(), total=len(df), desc="Batch Progress", unit="scenario"):
    scenario_name = row["scenario"]

    if scenario_name not in SCENARIOS:
        print(f"Skipping unknown scenario '{scenario_name}'")
        continue

    beta_within = SCENARIOS[scenario_name]["beta_within"]
    beta_cross = SCENARIOS[scenario_name]["beta_cross"]

    initial_infectious = int(row["initial_infectious"])
    initial_latent = int(row["initial_latent"])
    mortality = float(row["mortality"])
    reactivation = float(row["reactivation"])
    repeats = int(row["repeats"])
    days = int(row["days"])
    cores = int(row["cores"]) if "cores" in row and not pd.isna(row["cores"]) else 10

    print(f"\n--- Running scenario: {scenario_name} | m={mortality} | i={initial_infectious} | l={initial_latent} ---")
    print(f"Beta: within={beta_within}, cross={beta_cross} | Using {cores} cores.")

    results = run_simulation(
        initial_infectious=initial_infectious,
        initial_latent=initial_latent,
        beta_within=beta_within,
        beta_cross=beta_cross,
        mortality_rate=mortality,
        reactivation_daily_p=reactivation,
        repeats=repeats,
        days=days,
        n_cores=cores
    )

    outfile = f"results/{scenario_name}_m{mortality}_i{initial_infectious}_l{initial_latent}.npy"
    np.save(outfile, results)
    print(f"Saved: {outfile}")