# src/seildr_sim/path_resolver.py

import os
from pathlib import Path

# Resolve project root relative to this file location
PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

def resolve_scenarios_path():
    return PROJECT_ROOT / "src" / "seildr_sim" / "scenarios" / "scenarios.csv"

def resolve_results_dir():
    path = PROJECT_ROOT / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path

def resolve_logs_dir():
    path = PROJECT_ROOT / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path
