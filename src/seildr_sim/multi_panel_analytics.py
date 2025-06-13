#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi_panel_analytics.py — Clean version: heatmaps, thresholds, stability plots

Author: Julen Gamboa
Date: 06/2025
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from seildr_sim.path_resolver import resolve_summary_path

# -----------------------------------------------------
# Load aggregated data
# -----------------------------------------------------

summary_file = resolve_summary_path()
df = pd.read_csv(summary_file)

# -----------------------------------------------------
# Master output directories
# -----------------------------------------------------

os.makedirs("results/summaries/heatmaps/latent", exist_ok=True)
os.makedirs("results/summaries/heatmaps/infectious", exist_ok=True)
os.makedirs("results/summaries/thresholds", exist_ok=True)
os.makedirs("results/summaries/stability", exist_ok=True)

scenarios = sorted(df['scenario'].unique())

# -----------------------------------------------------
# 1. HEATMAPS — LATENT & INFECTIOUS
# -----------------------------------------------------

for scenario in scenarios:
    subset = df[df['scenario'] == scenario]

    infectious_levels = sorted(subset['initial_infectious'].unique())
    for infectious in infectious_levels:
        subsub = subset[subset['initial_infectious'] == infectious]
        pivot = subsub.pivot_table(index="initial_latent", columns="mortality", values="mean_deaths")

        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis", cbar_kws={"label": "Mean deaths"})
        plt.title(f"{scenario} | Infectious={infectious} (Mortality vs Latent)")
        plt.ylabel("Initial Latent")
        plt.xlabel("Mortality")
        plt.tight_layout()
        outfile = f"results/summaries/heatmaps/latent/{scenario}_i{infectious}_heatmap_latent.png"
        plt.savefig(outfile, dpi=300)
        plt.close()

    latent_levels = sorted(subset['initial_latent'].unique())
    for latent in latent_levels:
        subsub = subset[subset['initial_latent'] == latent]
        pivot = subsub.pivot_table(index="initial_infectious", columns="mortality", values="mean_deaths")

        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis", cbar_kws={"label": "Mean deaths"})
        plt.title(f"{scenario} | Latent={latent} (Mortality vs Infectious)")
        plt.ylabel("Initial Infectious")
        plt.xlabel("Mortality")
        plt.tight_layout()
        outfile = f"results/summaries/heatmaps/infectious/{scenario}_l{latent}_heatmap_infectious.png"
        plt.savefig(outfile, dpi=300)
        plt.close()

# -----------------------------------------------------
# 2. THRESHOLD MAPS (Extinction vs outbreak)
# -----------------------------------------------------

threshold = 20
for scenario in scenarios:
    subset = df[df['scenario'] == scenario].copy()
    subset["extinct"] = subset["mean_deaths"] < threshold

    pivot = subset.pivot_table(index="initial_latent", columns="mortality", values="extinct")

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="coolwarm", cbar_kws={"label": "Extinction (1=stable, 0=outbreak)"})
    plt.title(f"{scenario} — Extinction zones (threshold={threshold})")
    plt.ylabel("Initial Latent")
    plt.xlabel("Mortality")
    plt.tight_layout()
    outfile = f"results/summaries/thresholds/{scenario}_extinction_map.png"
    plt.savefig(outfile, dpi=300)
    plt.close()

# -----------------------------------------------------
# 3. STABILITY MAPS (variance zones)
# -----------------------------------------------------

for scenario in scenarios:
    subset = df[df['scenario'] == scenario]
    infectious_levels = sorted(subset['initial_infectious'].unique())

    for infectious in infectious_levels:
        subsub = subset[subset['initial_infectious'] == infectious]
        pivot = subsub.pivot_table(index="initial_latent", columns="mortality", values="std_deaths")

        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="mako_r", cbar_kws={"label": "Std deviation of deaths"})
        plt.title(f"{scenario} | Infectious={infectious} — Stability map")
        plt.ylabel("Initial Latent")
        plt.xlabel("Mortality")
        plt.tight_layout()
        outfile = f"results/summaries/stability/{scenario}_i{infectious}_stability_map.png"
        plt.savefig(outfile, dpi=300)
        plt.close()

print("\nMulti-panel analytics complete.")