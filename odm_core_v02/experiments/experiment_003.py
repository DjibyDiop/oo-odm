"""
OdM — Expérience 003 : Machine de Découverte

Exploration exhaustive (limitée) de toutes les séquences d'opérations
sur l'état initial. Lorsqu'une trajectoire produit une émergence ★,
le moteur s'arrête sur cette branche et la classifie.

Paramètres :
  max_depth   : profondeur max de la séquence d'opérations (ex: 3)
  max_branches: nombre de trajectoires à explorer

Rapport final :
  - Nombre de trajectoires explorées
  - Nombre d'émergences détectées
  - Classification de chaque émergence
"""

import sys
import os
import copy
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from odm_core_v02.odm.engine import OdMCore
from odm_core_v02.odm.element import CIRCLE, TRIANGLE, SQUARE
from odm_core_v02.odm.rules import RulesEngine, Emergence


# ============================================================
# UTILITAIRES
# ============================================================

def _fresh_odm() -> OdMCore:
    """Retourne un OdMCore vierge avec l'état initial canonique."""
    odm = OdMCore()
    odm.add_element("A", CIRCLE,   {"energie": 10})
    odm.add_element("B", TRIANGLE, {"matiere": 20})
    odm.add_element("C", SQUARE,   {"limite":  30})
    return odm


# ============================================================
# MACHINE DE DÉCOUVERTE
# ============================================================

def run_experiment_003(
    max_depth: int = 3,
    max_branches: int = 60,
    verbose: bool = True
) -> dict:
    """
    Machine de découverte exhaustive : explore des trajectoires de longueur
    max_depth sur l'état initial, et caractérise toutes les émergences ★.
    """

    if verbose:
        print("\n" + "="*64)
        print("  OdM — EXPÉRIENCE 003 : MACHINE DE DÉCOUVERTE")
        print(f"  Profondeur max : {max_depth}  |  Branches max : {max_branches}")
        print("="*64)

    discovered_emergences: list[Emergence] = []
    trajectories_explored = 0
    trajectories_with_emergence = 0

    # Chaque branche est une trajectoire indépendante
    # On les génère séquentiellement avec des graines différentes
    # pour diversifier les chemins explorés
    for branch_seed in range(max_branches):
        odm = _fresh_odm()
        engine = RulesEngine(
            strategy=RulesEngine.STRATEGY_RANDOM,
            seed=branch_seed
        )

        trajectory_actions = []
        branch_emergences = []

        for depth in range(max_depth):
            actions = engine.compute_actions(odm)
            if not actions:
                break

            action = engine.select_action(actions, odm)
            if action is None:
                break

            try:
                engine.execute_action(odm, action)
                trajectory_actions.append(str(action))
            except Exception:
                break

            emergence = engine.detect_emergence(odm, action, depth + 1)
            if emergence:
                branch_emergences.append(emergence)
                discovered_emergences.append(emergence)
                break  # Une émergence par trajectoire suffit

        trajectories_explored += 1
        if branch_emergences:
            trajectories_with_emergence += 1

        if verbose and branch_seed % 10 == 0:
            pct = (trajectories_with_emergence / max(1, trajectories_explored)) * 100
            print(
                f"  [branche {branch_seed:03d}] "
                f"Explorées: {trajectories_explored} | "
                f"★: {trajectories_with_emergence} ({pct:.0f}%)"
            )

    # --------------------------------------------------------
    # Déduplique les émergences par type
    # --------------------------------------------------------
    by_type: dict = {}
    for em in discovered_emergences:
        key = em.type.value
        by_type.setdefault(key, []).append(em)

    # --------------------------------------------------------
    # Rapport final
    # --------------------------------------------------------
    if verbose:
        print("\n" + "="*64)
        print("  RAPPORT MACHINE DE DÉCOUVERTE")
        print("="*64)
        print(f"  Trajectoires explorées     : {trajectories_explored}")
        print(f"  Trajectoires avec ★        : {trajectories_with_emergence}")
        print(f"  Total émergences détectées : {len(discovered_emergences)}")
        print()
        print("  Classification des émergences :")
        for etype, ems in by_type.items():
            print(f"    [{etype}] — {len(ems)} occurrence(s)")
            for em in ems[:2]:  # Affiche max 2 exemples par type
                print(
                    f"      • {em.description} "
                    f"(t={em.cycle}, via {em.trigger_operation})"
                )

        print()
        print("  Questions générées par la machine :")
        qs = _generate_questions(by_type)
        for q in qs:
            print(f"  ★ {q}")
        print()

    return {
        "trajectories_explored":        trajectories_explored,
        "trajectories_with_emergence":  trajectories_with_emergence,
        "emergences_total":             len(discovered_emergences),
        "emergences_by_type":           {k: len(v) for k, v in by_type.items()},
    }


def _generate_questions(by_type: dict) -> list:
    """
    Génère les questions que la machine de découverte pose à OO
    suite à ses émergences.
    """
    questions = []
    if "NOUVELLE_ORGANISATION" in by_type:
        questions.append(
            "Est-ce que cette topologie relationnelle inédite est reproductible ?"
        )
    if "NOUVEAU_BLOC" in by_type:
        questions.append(
            "Le bloc fils produit par division peut-il acquérir des capacités "
            "que l'original ne possédait pas ?"
        )
    if "NOUVELLE_CAPACITE" in by_type:
        questions.append(
            "Quelle opération déclenche systématiquement cette capacité ?"
        )
    if "NOUVELLE_FORME" in by_type:
        questions.append(
            "La forme ★ est-elle stable ou transitoire ?"
        )
    if not questions:
        questions.append(
            "Toutes les trajectoires mènent à des transformations connues. "
            "Faut-il enrichir le vocabulaire des formes ?"
        )
    return questions


if __name__ == "__main__":
    run_experiment_003(max_depth=3, max_branches=80, verbose=True)
