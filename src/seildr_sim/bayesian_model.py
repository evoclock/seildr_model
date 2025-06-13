#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bayesian_model.py
PyMC5 Bayesian Inference Model for SEILDR — Latent Herpesvirus Inference

This module defines a simplified Bayesian model for estimating transmission,
mortality, latency and reactivation parameters from cumulative death trajectories.
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from seildr_sim.path_resolver import resolve_results_path

# Load observed data (simulated or empirical cumulative deaths)
data_path = resolve_results_path("simulation_results.csv")
data = pd.read_csv(data_path, index_col="Day")
observed_cumulative_deaths = data.mean(axis=1).values
n_days = len(observed_cumulative_deaths)

# PyMC model
with pm.Model() as model:

    beta_within = pm.Uniform("beta_within", lower=0.2, upper=0.6)
    beta_cross = pm.Uniform("beta_cross", lower=0.0, upper=0.05)
    mortality_rate = pm.Beta("mortality_rate", alpha=2, beta=2)
    latent_fraction = pm.Uniform("latent_fraction", lower=0.0, upper=0.8)
    reactivation_rate = pm.Uniform("reactivation_rate", lower=0.0, upper=0.001)

    aviary_sizes = np.array([13, 14, 12, 15, 13, 13, 13, 36])
    total_birds = np.sum(aviary_sizes)
    incubation_days = 5
    infectious_days = 10

    latent_initial = pm.math.round(latent_fraction * total_birds)
    susceptible_initial = total_birds - latent_initial - 1
    exposed_initial = 0
    infectious_initial = 1
    dead_initial = 0

    S, E, I, L, D = [susceptible_initial], [exposed_initial], [infectious_initial], [latent_initial], [dead_initial]

    for t in range(1, n_days):
        lambda_within = beta_within * I[-1] / total_birds
        lambda_cross = beta_cross * I[-1] / total_birds
        lambda_total = lambda_within + lambda_cross

        new_exposed = lambda_total * S[-1]
        new_exposed = pm.math.minimum(new_exposed, S[-1])

        exposed_to_infectious = E[-1] / incubation_days
        infectious_outcomes = I[-1] / infectious_days
        deaths = mortality_rate * infectious_outcomes
        latent = (1 - mortality_rate) * infectious_outcomes
        reactivations = reactivation_rate * L[-1]

        S.append(S[-1] - new_exposed)
        E.append(E[-1] + new_exposed - exposed_to_infectious)
        I.append(I[-1] + exposed_to_infectious + reactivations - infectious_outcomes)
        L.append(L[-1] + latent - reactivations)
        D.append(D[-1] + deaths)

    cumulative_deaths = pm.math.stack(D)
    sigma = pm.HalfNormal("sigma", 5)
    pm.Normal("obs", mu=cumulative_deaths, sigma=sigma, observed=observed_cumulative_deaths)
