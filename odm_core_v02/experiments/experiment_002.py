"""
OdM — Expérience 002 : Boucle d'évolution autonome

Le moteur tourne N cycles.
À chaque cycle :
  1. CARACTÉRISATION de tous les éléments
  2. Calcul des possibilités (RulesEngine.compute_actions)
  3. Sélection RANDOM d'une action
  4. Exécution
  5. Détection d'émergence ★

Le moteur s'arrête si :
  - Plus aucune action possible
  - Une émergence ★ est détectée (mode "stop_on_emergence")
  - N cycles atteints
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from odm_core_v02.odm.engine import OdMCore
from odm_core_v02.odm.element import CIRCLE, TRIANGLE, SQUARE
from odm_core_v02.odm.rules import RulesEngine, RulesEngine


def run_experiment_002(
    n_cycles: int = 12,
    stop_on_emergence: bool = False,
    seed: int = 42,
    verbose: bool = True
) -> dict:
    """
    Boucle d'évolution autonome sur N cycles.
    """

    odm = OdMCore()
    engine = RulesEngine(strategy=RulesEngine.STRATEGY_RANDOM, seed=seed)

    # État initial (identique à Exp001)
    odm.add_element("A", CIRCLE,   {"energie": 10})
    odm.add_element("B", TRIANGLE, {"matiere": 20})
    odm.add_element("C", SQUARE,   {"limite":  30})

    if verbose:
        print("\n" + "="*60)
        print("  OdM — EXPÉRIENCE 002 : BOUCLE AUTONOME")
        print(f"  Stratégie : RANDOM  |  Cycles max : {n_cycles}")
        print("="*60)
        print(f"\n  État initial :")
        for e in odm.elements.values():
            print(f"    {e}")

    emergences = []
    actions_executed = []
    cycles_run = 0

    for cycle in range(1, n_cycles + 1):
        cycles_run = cycle

        # 1. Calcul des possibilités
        actions = engine.compute_actions(odm)

        if not actions:
            if verbose:
                print(f"\n  [cycle {cycle}] Plus aucune action possible. Arrêt.")
            break

        # 2. Sélection RANDOM
        action = engine.select_action(actions, odm)

        if verbose:
            print(f"\n  [cycle {cycle:02d}] {len(actions)} possibles → choisi : {action}")

        # 3. Exécution
        try:
            result = engine.execute_action(odm, action)
            actions_executed.append(str(action))
        except Exception as exc:
            if verbose:
                print(f"           [ÉCHEC] {exc}")
            continue

        # 4. Détection émergence
        emergence = engine.detect_emergence(odm, action, cycle)
        if emergence:
            emergences.append(emergence)
            if verbose:
                print(engine.classify_emergence(emergence))
            if stop_on_emergence:
                if verbose:
                    print(f"  [stop_on_emergence=True] Arrêt après ★.")
                break

    # --------------------------------------------------------
    # Résumé
    # --------------------------------------------------------
    if verbose:
        print("\n" + "="*60)
        print("  RÉSUMÉ EXPÉRIENCE 002")
        print("="*60)
        print(f"  Cycles exécutés    : {cycles_run}")
        print(f"  Actions exécutées  : {len(actions_executed)}")
        print(f"  Émergences ★       : {len(emergences)}")
        for em in emergences:
            print(f"    {em}")
        print(f"  Éléments finaux    : {len(odm.elements)}")
        print(f"  Relations finales  : {len(odm.relations)}")
        print(f"  Organisations      : {len(odm.organisations)}")
        print()

    return {
        "cycles_run":         cycles_run,
        "actions_executed":   len(actions_executed),
        "emergences_count":   len(emergences),
        "emergences":         [str(e) for e in emergences],
        "elements_final":     len(odm.elements),
        "relations_final":    len(odm.relations),
        "organisations_final": len(odm.organisations),
        "journal_length":     len(odm.event_log),
    }


if __name__ == "__main__":
    run_experiment_002(n_cycles=15, stop_on_emergence=False, verbose=True)
