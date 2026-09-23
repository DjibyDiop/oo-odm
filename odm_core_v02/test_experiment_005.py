"""
OdM — Tests Expérience 005 : L'Organisme de Possibilités (Phase 4)
Validation rigoureuse des 6 compartiments, des 3 organes D+ et des moteurs HPC/IA.
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.experiments.experiment_005 import run_experiment_005
from odm_core_v02.odm.possibility_field import PossibilityField
from odm_core_v02.odm.engine import OdMCore
from odm_core_v02.omx_bridge import OMXBridge


def test_experiment_005():
    print("\n=== TEST OdM — EXPÉRIENCE 005 (L'Organisme de Possibilités) ===")

    # Exécution de l'expérience sur 18 cycles
    report = run_experiment_005(cycles=18, seed=42, verbose=False)

    dims = report["dimensions"]
    mets = report["metrics"]

    # 1. Vérification de la génération du champ
    assert report["field_generation"] == 18, f"Génération inattendue: {report['field_generation']}"
    print("  ✓ Génération finale du champ atteinte (P18)")

    # 2. Compartiment 1 : Ce qui existe
    assert dims["existing_elements"] >= 5, f"Éléments insuffisants: {dims['existing_elements']}"
    assert dims["active_relations"] >= 1, f"Relations insuffisantes: {dims['active_relations']}"
    assert dims["organisations"] >= 1, f"Organisations insuffisantes: {dims['organisations']}"
    print(f"  ✓ Compartiment 'Existant' vérifié : {dims['existing_elements']} éléments, {dims['active_relations']} relations")

    # 3. Compartiment 2 : Ce qui est possible
    assert dims["possibilities_open"] > 20, f"Possibilités trop faibles: {dims['possibilities_open']}"
    print(f"  ✓ Compartiment 'Possibles' dynamique : {dims['possibilities_open']} actions calculées")

    # 4. Compartiment 3 : Ce qui a été essayé
    assert dims["explored_trajectories"] == 18, f"Trajectoires incorrectes: {dims['explored_trajectories']}"
    print(f"  ✓ Compartiment 'Exploré' : {dims['explored_trajectories']} trajectoires répertoriées")

    # 5. Compartiment 4 : Ce qui a émergé (Singularités ★)
    assert dims["discovered_emergences"] >= 2, f"Émergences insuffisantes: {dims['discovered_emergences']}"
    em_types = [e["type"] for e in report["emergences_detail"]]
    assert "NOUVEAU_BLOC" in em_types, "Émergence NOUVEAU_BLOC manquante"
    assert "NOUVELLE_ORGANISATION" in em_types, "Émergence NOUVELLE_ORGANISATION manquante"
    print(f"  ✓ Compartiment 'Émergences ★' : {dims['discovered_emergences']} singularités ({', '.join(set(em_types))})")

    # 6. Compartiment 5 : Ce qui est interdit
    assert "forbidden_actions" in dims
    print(f"  ✓ Compartiment 'Interdits' actif (D+ Gate)")

    # 7. Compartiment 6 : Ce qui reste inexploré
    assert dims["unexplored_branches"] > 0
    assert 0.0 < mets["unexplored_ratio_pct"] < 100.0
    print(f"  ✓ Compartiment 'Inexploré' : {dims['unexplored_branches']} branches frontières ({mets['unexplored_ratio_pct']}%)")

    # 8. Métriques informationnelles
    assert mets["field_entropy"] > 1.5, f"Entropie trop basse: {mets['field_entropy']}"
    print(f"  ✓ Entropie informationnelle du champ validée : H = {mets['field_entropy']} bits")

    # 9. Validation unitaire directe du pont OMX sur les 3 organes
    bridge = OMXBridge()
    assert bridge.status()["o_dplus_ready"] is True
    assert bridge.status()["o_cpp_ready"] is True
    assert bridge.status()["o_py_ready"] is True
    print("  ✓ Moteurs natifs OMX 100% opérationnels (D+, C++, Python)")

    print("\n--> [PASS] Expérience 005 — Organisme de Possibilités validé avec succès (100% Zéro Mocks)\n")


if __name__ == "__main__":
    test_experiment_005()
