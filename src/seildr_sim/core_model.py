#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_model.py — SEILDR stochastic model for chronic avian herpesvirus infection dynamics and management.

Implements:
- Latency
- Reactivation
- Cross-aviary vs within-aviary transmission
- Mortality variation
- Parallelized stochastic replicates (multiprocessing)

Author: Julen Gamboa
Date: 06/2025
"""

import numpy as np
from multiprocessing import Pool

def single_run(params):
    (
        initial_infectious, initial_latent, beta_within, beta_cross, 
        mortality_rate, reactivation_daily_p, days
    ) = params

    compartment_sizes = np.array([36, 11, 16, 8, 25, 10, 14, 7])
    n_compartments = len(compartment_sizes)

    S = compartment_sizes.copy()
    E, I, L, D = [np.zeros(n_compartments, dtype=int) for _ in range(4)]

    L += int(initial_latent)
    S -= int(initial_latent)

    I[0] = initial_infectious
    S[0] -= initial_infectious

    I_timers = [[] for _ in range(n_compartments)]
    E_timers = [[] for _ in range(n_compartments)]
    I_timers[0].extend([10] * initial_infectious)

    daily_deaths = []

    for day in range(days):
        deaths_today = 0
        for i in range(n_compartments):
            lambda_within = beta_within * I[i] / compartment_sizes[i]
            infectious_others = np.sum(I) - I[i]
            lambda_cross = beta_cross * infectious_others / np.sum(compartment_sizes)
            lambda_total = lambda_within + lambda_cross

            S[i] = max(0, S[i])
            susceptibles = S[i]
            prob_infection = 1 - np.exp(-lambda_total)
            prob_infection = min(max(prob_infection, 0), 1)

            new_exposed = np.random.binomial(susceptibles, prob_infection)
            S[i] -= new_exposed
            E[i] += new_exposed
            E_timers[i].extend([5] * new_exposed)

            progressed, new_E_timers = [], []
            for t in E_timers[i]:
                t -= 1
                if t <= 0:
                    progressed.append(t)
                else:
                    new_E_timers.append(t)
            E_timers[i] = new_E_timers
            E[i] -= len(progressed)
            I[i] += len(progressed)
            I_timers[i].extend([10] * len(progressed))

            finished, new_I_timers = [], []
            for t in I_timers[i]:
                t -= 1
                if t <= 0:
                    finished.append(t)
                else:
                    new_I_timers.append(t)
            I_timers[i] = new_I_timers
            I[i] -= len(finished)

            for _ in finished:
                if np.random.rand() < mortality_rate:
                    D[i] += 1
                    deaths_today += 1
                else:
                    L[i] += 1

            reactivations = np.random.binomial(L[i], reactivation_daily_p)
            L[i] -= reactivations
            I[i] += reactivations
            I_timers[i].extend([10] * reactivations)

        daily_deaths.append(deaths_today)

    return daily_deaths

def run_simulation(
    initial_infectious=7, 
    initial_latent=30, 
    beta_within=0.1, 
    beta_cross=0.02, 
    mortality_rate=0.15, 
    reactivation_daily_p=1/3650, 
    repeats=500, 
    days=1095, 
    n_cores=10
):
    """
    Runs multiple stochastic replicates in parallel.

    Returns:
        numpy.ndarray: shape (repeats, days) cumulative daily deaths.
    """
    with Pool(processes=n_cores) as pool:
        param_list = [(initial_infectious, initial_latent, beta_within, beta_cross,
                       mortality_rate, reactivation_daily_p, days)] * repeats
        results = pool.map(single_run, param_list)
    return np.array(results)
