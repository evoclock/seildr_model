#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inference_runner.py
Run Bayesian inference on exported simulation output.

Author: Julen Gamboa
Date: 06/2025
"""

import pymc as pm
import arviz as az
import pandas as pd
from seildr_sim import bayesian_model
import matplotlib.pyplot as plt
import os

# Output directory
os.makedirs("results/summaries", exist_ok=True)

print("Running Bayesian inference...")

with bayesian_model.model:
    trace = pm.sample(4000, tune=4000, target_accept=0.95, cores=10)

az.plot_trace(trace)
plt.show()

summary = az.summary(trace)
print(summary)

# Save results always inside /results/summaries/
output_file = "results/summaries/bayesian_inference_summary.csv"
summary.to_csv(output_file)

print(f"\nInference complete. Summary saved to {output_file}")

