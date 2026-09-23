"""
OdM — Expérience 005 : L'Organisme de Possibilités en Action (Phase 4)

Vision ultime de plan.md (lignes 14548-14665) :
  L'Organisme de Possibilités (Possibility Field) est un instrument vivant qui
  maintient dynamiquement la représentation des 6 compartiments fondamentaux :
    1. Ce qui existe       (éléments réels, relations, organisations)
    2. Ce qui est possible   (actions combinatoires calculées en temps réel)
    3. Ce qui a été essayé   (trajectoires explorées)
    4. Ce qui a émergé       (singularités ★ classifiées)
    5. Ce qui est interdit   (verdicts FORBID D+, lois d'incompatibilité)
    6. Ce qui reste inexploré (front de découverte, ratio d'inconnu)

Couplage avec OMX (Zéro Mocks) :
  - O-D+ : Constitution SandBox, Ontologie des 4 formes, Suivi du champ
  - O-CPP: Accélération combinatoire HPC de l'arbre des possibles
  - O-PY : Entropie de Shannon des signatures et motifs
"""

import sys
import os
import json
import random

# Configuration encodage et imports
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from odm_core_v02.odm.element import CIRCLE, TRIANGLE, SQUARE, STAR
from odm_core_v02.odm.engine import OdMCore
from odm_core_v02.odm.possibility_field import PossibilityField
from odm_core_v02.omx_bridge import OMXBridge


def run_experiment_005(cycles: int = 18, seed: int = 42, verbose: bool = True) -> dict:
    random.seed(seed)

    if verbose:
        print("\n" + "=" * 68)
        print("  OdM — EXPÉRIENCE 005 : L'ORGANISME DE POSSIBILITÉS (PHASE 4)")
        print("  Champ Dynamique P₀ → P_k | 3 Organes D+ | O-CPP HPC | O-PY Entropie")
        print("=" * 68)

    # Initialisation du pont natif OMX (Zéro Mocks)
    bridge = OMXBridge(verbose=False)
    status = bridge.status()
    if verbose:
        print(f"\n[OMX] Moteurs natifs connectés : {status}")

    # Création du noyau OdM initial
    core = OdMCore()
    core.add_element("A", CIRCLE, {"energie": 10})
    core.add_element("B", TRIANGLE, {"matiere": 20})
    core.add_element("C", SQUARE, {"limite": 30})

    # Validation Ontologique Biologique initiale via odm_ontology.plus
    ontology_valid = bridge.validate_ontology(core.elements)
    if verbose:
        print(f"[O-D+] Validation Ontologique Biologique initiale : {'VALIDÉ' if ontology_valid else 'ÉCHEC'}")

    # Instanciation de l'Organisme de Possibilités
    field = PossibilityField(core=core, bridge=bridge, seed=seed)

    if verbose:
        print("\n--- CHAMP INITIAL P₀ ---")
        p0 = field.history[0]
        print(f"  Éléments existants        : {p0.element_count}")
        print(f"  Possibilités ouvertes     : {p0.possible_actions_count}")
        print(f"  Entropie initiale         : {p0.entropy}")
        print(f"  Ratio inexploré           : {p0.unexplored_ratio}%\n")

    # Évolution autonome du champ à travers N transitions P_k -> P_{k+1}
    for step_idx in range(1, cycles + 1):
        step_res = field.evolve_step(strategy="RANDOM")
        status = step_res.get("status")

        if verbose:
            gen = field.generation
            act_desc = step_res.get("action", "?")
            print(f"  [P{gen:02d}] {act_desc} → {status}")

        # Détection d'émergence
        em = step_res.get("emergence")
        if em and verbose:
            em_type = em.type.value if hasattr(em.type, "value") else str(em.type)
            em_action = f"{em.trigger_operation}({', '.join(em.trigger_targets)})"
            print(f"\n  ★ ÉMERGENCE DÉTECTÉE (P{field.generation}) ★")
            print(f"  ├── Type       : {em_type}")
            print(f"  ├── Description: {em.description}")
            print(f"  └── Action     : {em_action}\n")

        # Tous les 6 cycles : synchronisation approfondie avec O-CPP et O-PY
        if step_idx % 6 == 0:
            # 1. Calcul HPC combinatoire
            elem_count = len(field.core.elements)
            hpc_res = bridge.expand_tree(depth=3, element_count=elem_count)
            traj_hpc = hpc_res.get("valid_trajectories", 0)

            # 2. Calcul d'entropie informationnelle O-PY
            sigs = [f"{el.form}:{el.id}" for el in field.core.elements.values()]
            opy_entropy = bridge.compute_field_entropy(sigs)

            if verbose:
                print(f"       [O-CPP HPC @ P{field.generation}] {elem_count} éléments → {traj_hpc} trajectoires valides")
                print(f"       [O-PY Information @ P{field.generation}] Entropie structurelle = {opy_entropy}")

    # Exportation du Rapport Scientifique complet pour OO
    report = field.export_scientific_report()

    if verbose:
        print("\n" + "=" * 68)
        print("  RAPPORT SCIENTIFIQUE FINAL DE L'ORGANISME DE POSSIBILITÉS (POUR OO)")
        print("=" * 68)
        dims = report["dimensions"]
        mets = report["metrics"]
        print(f"  Génération finale du champ : P{report['field_generation']}")
        print(f"  Éléments existants         : {dims['existing_elements']}")
        print(f"  Relations actives          : {dims['active_relations']}")
        print(f"  Organisations              : {dims['organisations']}")
        print(f"  Possibilités ouvertes      : {dims['possibilities_open']}")
        print(f"  Trajectoires explorées     : {dims['explored_trajectories']}")
        print(f"  Émergences découvertes ★   : {dims['discovered_emergences']}")
        print(f"  Actions interdites (D+)    : {dims['forbidden_actions']}")
        print(f"  Branches inexplorées       : {dims['unexplored_branches']}")
        print(f"  Entropie du champ          : {mets['field_entropy']}")
        print(f"  Ratio inexploré            : {mets['unexplored_ratio_pct']}%")
        print(f"  Champ saturé (>100 traj)   : {mets['is_saturated']}")

        print("\n  Détail des singularités découvertes retournées à OO :")
        for em in report["emergences_detail"]:
            print(f"    • [{em['type']}] P{em['cycle']} via {em['action']} : {em['description']}")

        print("\n" + "=" * 68 + "\n")

    return report


if __name__ == "__main__":
    run_experiment_005()
