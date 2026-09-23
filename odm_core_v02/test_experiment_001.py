"""
OdM — Tests Expérience 001 (Séquence canonique)
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.experiments.experiment_001 import run_experiment_001


def test_experiment_001():
    print("\n=== TEST OdM — EXPÉRIENCE 001 (Séquence Canonique) ===\n")

    report = run_experiment_001(verbose=True)

    # Vérifications clés du plan.md
    assert report["B_divided"],           "B doit être divisé"
    assert report["B1_exists"],           "B1 doit exister après division"
    assert report["B2_exists"],           "B2 doit exister après division"
    assert report["R1_broken"],           "R1 doit être rompue après RUPTURE"
    assert report["A_contains_C"],        "A doit contenir C après CONTENIR"
    assert report["organisation_ABC"],    "Organisation O1(A,B,C) doit exister"
    assert report["snap_A_energie"] == 25, f"Énergie de A = 25, obtenu {report['snap_A_energie']}"
    assert report["elements_count"] >= 5,  "≥5 éléments (A,B,C,B1,B2)"
    assert report["journal_length"] >= 7,  "Journal ≥7 événements"

    print("\n--> [PASS] Expérience 001 — Séquence Canonique validée.")

if __name__ == "__main__":
    test_experiment_001()
