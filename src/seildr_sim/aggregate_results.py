#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggregate_results.py — Aggregate all SEILDR model outputs into summary table
"""

import numpy as np
import pandas as pd
import os
import glob
import re

# Output directory for CSV summaries
os.makedirs("results/summaries", exist_ok=True)

# Metadata extraction helper
def extract_metadata(filename):
    basename = os.path.basename(filename)
    match = re.match(r"(.*?)_m([0-9.]+)_i(\d+)_l(\d+)\.npy", basename)
    if not match:
        return None
    scenario, mortality, infectious, latent = match.groups()
    return scenario, float(mortality), int(infectious), int(latent)

records = []
files = glob.glob("results/*.npy")

if not files:
    print("No simulation result files found in /results/")
else:
    for filepath in sorted(files):
        meta = extract_metadata(filepath)
        if not meta:
            print(f"Skipping unrecognized file: {filepath}")
            continue

        scenario, mortality, infectious, latent = meta
        results = np.load(filepath)
        cumulative = np.cumsum(results, axis=1)
        final_cumulative = cumulative[:, -1]

        mean_final = np.mean(final_cumulative)
        lower_final = np.percentile(final_cumulative, 2.5)
        upper_final = np.percentile(final_cumulative, 97.5)
        std_final = np.std(final_cumulative)

        records.append({
            "scenario": scenario,
            "mortality": mortality,
            "initial_infectious": infectious,
            "initial_latent": latent,
            "mean_deaths": mean_final,
            "lower_deaths": lower_final,
            "upper_deaths": upper_final,
            "std_deaths": std_final
        })

    df = pd.DataFrame(records)
    out_path = "results/summaries/aggregate_summary.csv"
    df.to_csv(out_path, index=False)
    print(f"Aggregated {len(df)} simulation results into {out_path}")

