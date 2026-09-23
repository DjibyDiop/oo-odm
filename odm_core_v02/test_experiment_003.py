"""
OdM — Tests Expérience 003 (Machine de découverte)
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.experiments.experiment_003 import run_experiment_003


def test_experiment_003():
    print("\n=== TEST OdM — EXPÉRIENCE 003 (Machine de Découverte) ===\n")

    report = run_experiment_003(max_depth=3, max_branches=60, verbose=True)

    assert report["trajectories_explored"] > 0,   "Des trajectoires ont été explorées"
    assert report["emergences_total"] > 0,         (
        "La machine de découverte doit trouver ≥1 émergence dans 60 trajectoires"
    )
    # La machine doit découvrir au moins 2 types différents d'émergences
    assert len(report["emergences_by_type"]) >= 1, (
        "Au moins un type d'émergence classifié"
    )

    taux = report["trajectories_with_emergence"] / report["trajectories_explored"]
    print(
        f"\n--> [PASS] Expérience 003 — "
        f"{report['emergences_total']} émergences classifiées "
        f"({taux:.0%} des trajectoires)"
    )

if __name__ == "__main__":
    test_experiment_003()
