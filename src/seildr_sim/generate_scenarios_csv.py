#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_scenarios_csv.py — Automated grid generator for scenarios.csv

Author: Julen Gamboa
Date: 06/2025
"""

import pandas as pd
import itertools
from seildr_sim.path_resolver import resolve_scenarios_path

# ---------------------------------------------------
# Define experiment ranges
# ---------------------------------------------------

scenarios = ["do_nothing", "isolation_only", "isolation_biosecurity"]

mortality_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
initial_infectious_values = [2, 5, 10, 15]
initial_latent_values = [10, 20, 30, 40, 50]

# Fixed global parameters
reactivation = 0.00027
repeats = 3000
days = 1095
cores = 10

# ---------------------------------------------------
# Generate full design grid
# ---------------------------------------------------

rows = []

for scenario, mortality, infectious, latent in itertools.product(
    scenarios, mortality_values, initial_infectious_values, initial_latent_values
):
    row = {
        "scenario": scenario,
        "initial_infectious": infectious,
        "initial_latent": latent,
        "mortality": mortality,
        "reactivation": reactivation,
        "repeats": repeats,
        "days": days,
        "cores": cores
    }
    rows.append(row)

df = pd.DataFrame(rows)

# Use the path resolver to always write into src/seildr_sim/scenarios/
scenarios_path = resolve_scenarios_path()
df.to_csv(scenarios_path, index=False)

print(f"Generated scenarios.csv with {len(df)} rows at {scenarios_path}")

