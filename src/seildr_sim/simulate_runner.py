#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulate_runner.py — Interactive + CLI runner for SEILDR simulation

Author: Julen Gamboa
Date: 06/2025

Description:
---------------------------------------
Dual-purpose entrypoint allowing either:
- Fully interactive mode (if no CLI arguments are provided)
- CLI-driven batch execution for direct reproducibility

Usage examples:
---------------------------------------
1. Interactive mode:
    python simulate_runner.py

2. CLI mode:
    python simulate_runner.py --scenario isolation_only --initial_infectious 5 --initial_latent 30 --mortality 0.4 --repeats 1000 --days 1500 --cores 8

Output:
---------------------------------------
- Stores .npy files into /results/
- Logs run details into /logs/simulation.log
"""

import argparse
import numpy as np
import os
import logging
from seildr_sim.core_model import run_simulation

# Create output and logs directories if missing
os.makedirs("results", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(filename="logs/simulation.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Management scenario mapping (consistent with full batch pipeline)
SCENARIOS = {
    "do_nothing": {"beta_within": 0.3, "beta_cross": 0.02},
    "isolation_only": {"beta_within": 0.15, "beta_cross": 0.01},
    "isolation_biosecurity": {"beta_within": 0.05, "beta_cross": 0.002}
}

def interactive_input(prompt, default, cast_fn):
    try:
        value = input(f"{prompt} [{default}]: ")
        return cast_fn(value) if value else default
    except:
        return default

def main():
    parser = argparse.ArgumentParser(description="Run SEILDR simulation for Pacheco's Disease")
    parser.add_argument("--scenario", type=str, choices=SCENARIOS.keys(), help="Management scenario")
    parser.add_argument("--initial_infectious", type=int, help="Initial infectious birds")
    parser.add_argument("--initial_latent", type=int, help="Initial latent carriers")
    parser.add_argument("--mortality", type=float, help="Mortality rate")
    parser.add_argument("--reactivation", type=float, help="Reactivation probability")
    parser.add_argument("--repeats", type=int, help="Number of replicates")
    parser.add_argument("--days", type=int, help="Number of days")
    parser.add_argument("--cores", type=int, help="CPU cores to use (max 10)")
    parser.add_argument("--output", type=str, help="Optional manual output file")

    args = parser.parse_args()

    if not any(vars(args).values()):
        print("\n--- Interactive Mode ---\n")
        print("Scenarios available:", list(SCENARIOS.keys()))
        scenario = interactive_input("Scenario", "do_nothing", str)
        if scenario not in SCENARIOS:
            print("Invalid scenario selected.")
            return

        initial_infectious = interactive_input("Initial infectious", 6, int)
        initial_latent = interactive_input("Initial latent carriers", 30, int)
        mortality = interactive_input("Mortality rate", 0.5, float)
        reactivation = interactive_input("Reactivation probability", 1/3650, float)
        repeats = interactive_input("Replicates", 500, int)
        days = interactive_input("Days", 1095, int)
        cores = interactive_input("Cores (max 10)", 10, int)

        default_filename = f"results/{scenario}_m{mortality}_i{initial_infectious}_l{initial_latent}.npy"
        output = interactive_input("Output file", default_filename, str)
    else:
        scenario = args.scenario or "do_nothing"
        initial_infectious = args.initial_infectious or 6
        initial_latent = args.initial_latent or 30
        mortality = args.mortality or 0.15
        reactivation = args.reactivation or 1/3650
        repeats = args.repeats or 500
        days = args.days or 1095
        cores = args.cores or 10

        output = args.output or f"results/{scenario}_m{mortality}_i{initial_infectious}_l{initial_latent}.npy"

    beta_within = SCENARIOS[scenario]["beta_within"]
    beta_cross = SCENARIOS[scenario]["beta_cross"]

    logging.info(f"Scenario: {scenario}")
    logging.info(f"Parameters: Infectious={initial_infectious}, Latent={initial_latent}, "
                 f"Mortality={mortality}, Reactivation={reactivation}, "
                 f"beta_within={beta_within}, beta_cross={beta_cross}, "
                 f"Repeats={repeats}, Days={days}, Cores={cores}")

    print(f"\nRunning scenario: {scenario} using {cores} cores...")

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

    np.save(output, results)
    logging.info(f"Simulation complete. Saved to {output}")

    cumulative = np.cumsum(results, axis=1)
    final_mean = np.mean(cumulative[:, -1])
    final_interval = np.percentile(cumulative[:, -1], [2.5, 97.5])

    print(f"Final cumulative deaths: {final_mean:.1f} [{final_interval[0]:.1f} - {final_interval[1]:.1f}]")
    print(f"Saved to {output}\n")

if __name__ == "__main__":
    main()
