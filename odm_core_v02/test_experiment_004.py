"""
OdM — Tests Expérience 004 (Boucle fermée OO ↔ OdM)
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.experiments.experiment_004 import run_experiment_004


def test_experiment_004():
    print("\n=== TEST OdM — EXPÉRIENCE 004 (Boucle Fermée OO ↔ OdM) ===\n")

    report = run_experiment_004(n_cycles=15, hpc_check_every=5, seed=7, verbose=True)

    # D+ doit avoir autorisé tous les cycles (SANDBOX = toujours ALLOW)
    assert report["cycles_authorized"] > 0,        "D+ doit avoir autorisé ≥1 cycle"
    assert report["cycles_blocked"] == 0,           "En SANDBOX tous les cycles sont ALLOW"
    assert report["actions_executed"] > 0,          "Des actions doivent être exécutées"

    # O-CPP HPC doit avoir été invoqué au moins une fois
    assert len(report["hpc_expansions"]) >= 1, (
        "O-CPP HPC doit être invoqué au moins une fois (tous les 5 cycles)"
    )

    # Au moins une expansion doit avoir produit des trajectoires
    max_traj = max(e["valid_trajectories"] for e in report["hpc_expansions"])
    assert max_traj > 0, f"O-CPP doit calculer >0 trajectoires, obtenu {max_traj}"

    # La boucle doit avoir produit des émergences
    assert report["emergences_count"] > 0, (
        "La boucle fermée doit générer ≥1 émergence"
    )

    # L'espace des possibles doit s'enrichir (512 trajectoires avec 5 éléments)
    final_exp = report["hpc_expansions"][-1]
    assert final_exp["valid_trajectories"] >= 8, (
        f"L'espace final doit être ≥8 trajectoires, obtenu {final_exp['valid_trajectories']}"
    )

    print(
        f"\n--> [PASS] Expérience 004 — Boucle fermée OO↔OdM validée : "
        f"{report['emergences_count']} ★, "
        f"{len(report['hpc_expansions'])} expansions HPC, "
        f"max {max_traj} trajectoires C++"
    )


if __name__ == "__main__":
    test_experiment_004()
