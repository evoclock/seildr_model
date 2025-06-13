#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_results.py — Interactive parser for SEILDR simulation results
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re

plt.style.use("seaborn-v0_8-muted")

def extract_metadata(filename):
    basename = os.path.basename(filename)
    match = re.match(r"(.*?)_m([0-9.]+)_i(\d+)_l(\d+)\.npy", basename)
    if not match:
        return None
    scenario, mortality, infectious, latent = match.groups()
    return scenario, float(mortality), int(infectious), int(latent)

def process_file(filepath, save=True):
    meta = extract_metadata(filepath)
    if not meta:
        print(f"Skipping unrecognized file: {filepath}")
        return
    scenario, mortality, infectious, latent = meta

    results = np.load(filepath)
    cumulative = np.cumsum(results, axis=1)

    mean_cum = np.mean(cumulative, axis=0)
    lower = np.percentile(cumulative, 2.5, axis=0)
    upper = np.percentile(cumulative, 97.5, axis=0)

    days = np.arange(len(mean_cum))

    plt.figure(figsize=(12, 7))
    plt.fill_between(days, lower, upper, color=plt.get_cmap("viridis")(0.3), alpha=0.4, label="95% interval")
    plt.plot(days, mean_cum, color=plt.get_cmap("viridis")(0.8), linewidth=2, label="Mean cumulative deaths")

    plt.title(f"Scenario: {scenario} | Mortality: {mortality} | Infectious: {infectious} | Latent: {latent}")
    plt.xlabel("Days")
    plt.ylabel("Cumulative Deaths")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")

    if save:
        summary_dir = "results/summaries"
        os.makedirs(summary_dir, exist_ok=True)
        outfile = os.path.join(summary_dir, f"{scenario}_m{mortality}_i{infectious}_l{latent}.png")
        plt.savefig(outfile, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {outfile}")

    plt.show()

def interactive_mode():
    files = sorted(glob.glob("results/*.npy"))

    if not files:
        print("No simulation result files found in /results/")
        return

    while True:
        print("\nAvailable simulation result files:\n")
        for idx, file in enumerate(files):
            print(f"[{idx}] {os.path.basename(file)}")

        choice = input("\nSelect file number to visualize (or 'q' to quit): ")
        if choice.lower() == 'q':
            break
        try:
            idx = int(choice)
            if idx < 0 or idx >= len(files):
                print("Invalid choice.")
                continue
            selected_file = files[idx]
            save = input("Save PNG output? [y/n]: ").lower().startswith("y")
            process_file(selected_file, save=save)
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    interactive_mode()


