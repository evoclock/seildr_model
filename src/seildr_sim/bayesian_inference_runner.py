#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bayesian_inference_runner.py
PyMC5 Inference Runner for SEILDR model — full multi-core sampling.
"""

import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import os
from seildr_sim import bayesian_model  # Package-relative import

# Ensure output directory exists
os.makedirs("results", exist_ok=True)

print("Starting Bayesian inference using PyMC5...")
with bayesian_model.model:
    trace = pm.sample(
        draws=4000, 
        tune=4000, 
        target_accept=0.95, 
        cores=10
    )

print("Sampling complete. Generating trace plots...")
az.plot_trace(trace)
plt.show()

summary = az.summary(trace)
print("\nPosterior Summary:\n", summary)

summary_path = "results/bayesian_inference_summary.csv"
summary.to_csv(summary_path)
print(f"\nSummary written to: {summary_path}")
