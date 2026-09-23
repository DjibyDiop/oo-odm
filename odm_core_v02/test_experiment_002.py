"""
OdM — Tests Expérience 002 (Boucle autonome)
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.experiments.experiment_002 import run_experiment_002


def test_experiment_002():
    print("\n=== TEST OdM — EXPÉRIENCE 002 (Boucle Autonome) ===\n")

    report = run_experiment_002(n_cycles=12, stop_on_emergence=False, seed=42, verbose=True)

    assert report["cycles_run"] > 0,          "Au moins un cycle exécuté"
    assert report["actions_executed"] > 0,    "Au moins une action exécutée"
    assert report["elements_final"] >= 3,     "Au moins 3 éléments dans l'état final"
    assert report["journal_length"] >= 3,     "Journal contient au moins 3 entrées"

    # La boucle autonome doit produire au moins une émergence en 12 cycles
    assert report["emergences_count"] > 0, (
        f"La boucle autonome doit produire ≥1 émergence en "
        f"{report['cycles_run']} cycles, obtenu {report['emergences_count']}"
    )

    print(f"\n--> [PASS] Expérience 002 — {report['emergences_count']} émergence(s) en {report['cycles_run']} cycles.")

if __name__ == "__main__":
    test_experiment_002()
