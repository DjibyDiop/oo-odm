"""
OdM — Expérience 004 : Boucle Fermée OO ↔ OdM (Phase 3)

La boucle fermée :
  OO (monde/données) → OdM (explore/transforme) → découvertes → OO

Concrètement :
  1. Avant chaque cycle : D+ autorise ou bloque via OMXBridge
  2. Si ALLOW : le moteur autonome (RANDOM) exécute l'action
  3. Chaque N cycles : O-CPP recalcule l'arbre complet des possibles
     et on compare avec ce que la boucle RANDOM a trouvé
  4. Les émergences ★ sont retournées à OO comme "nouvelles connaissances"

C'est la première boucle réelle OO ↔ OdM décrite dans plan.md (L14622-L14654).
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.odm.engine import OdMCore
from odm_core_v02.odm.element import CIRCLE, TRIANGLE, SQUARE
from odm_core_v02.odm.rules import RulesEngine, Emergence
from odm_core_v02.omx_bridge import OMXBridge


def run_experiment_004(
    n_cycles: int = 15,
    hpc_check_every: int = 5,
    seed: int = 7,
    verbose: bool = True
) -> dict:
    """
    Boucle fermée OO ↔ OdM avec arbitrage D+ et expansion HPC.
    """

    if verbose:
        print("\n" + "="*68)
        print("  OdM — EXPÉRIENCE 004 : BOUCLE FERMÉE OO ↔ OdM")
        print(f"  D+ gate actif | O-CPP HPC tous les {hpc_check_every} cycles")
        print("="*68)

    # --------------------------------------------------------
    # Initialisation
    # --------------------------------------------------------
    odm    = OdMCore()
    engine = RulesEngine(strategy=RulesEngine.STRATEGY_RANDOM, seed=seed)
    bridge = OMXBridge(verbose=False)

    odm.add_element("A", CIRCLE,   {"energie": 10})
    odm.add_element("B", TRIANGLE, {"matiere": 20})
    odm.add_element("C", SQUARE,   {"limite":  30})

    if verbose:
        print(f"\n  Pont OMX : {bridge.status()}")
        print(f"\n  État initial :")
        for e in odm.elements.values():
            print(f"    {e}")

    # --------------------------------------------------------
    # Compteurs
    # --------------------------------------------------------
    cycles_authorized  = 0
    cycles_blocked     = 0
    actions_executed   = []
    emergences         = []
    hpc_expansions     = []

    for cycle in range(1, n_cycles + 1):

        # 1. Gate D+ : OO autorise-t-il ce cycle ?
        authorized = bridge.authorize_cycle(
            cycle=cycle,
            elements=odm.elements,
            scope="SANDBOX"
        )

        if not authorized:
            cycles_blocked += 1
            if verbose:
                print(f"\n  [cycle {cycle:02d}] ★ BLOQUÉ par D+ (QUARANTINE/FORBID)")
            continue

        cycles_authorized += 1

        # 2. Calcul des possibilités + sélection RANDOM
        actions = engine.compute_actions(odm)
        if not actions:
            if verbose:
                print(f"\n  [cycle {cycle:02d}] Aucune action possible. Arrêt.")
            break

        action = engine.select_action(actions, odm)

        if verbose:
            print(
                f"\n  [cycle {cycle:02d}] D+=ALLOW | {len(actions)} possibles "
                f"→ choisi : {action}"
            )

        # 3. Exécution
        try:
            engine.execute_action(odm, action)
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

        # 5. Tous les N cycles : O-CPP recalcule l'arbre complet
        if cycle % hpc_check_every == 0:
            hpc_result = bridge.expand_tree(
                depth=3,
                element_count=len(odm.elements),
                relaxed=False
            )
            hpc_expansions.append({
                "cycle": cycle,
                "elements": len(odm.elements),
                "valid_trajectories": hpc_result.get("valid_trajectories", 0),
            })
            if verbose:
                vt = hpc_result.get("valid_trajectories", "?")
                print(
                    f"\n  [O-CPP HPC @ cycle {cycle}] "
                    f"{len(odm.elements)} éléments → "
                    f"{vt} trajectoires valides calculées par le moteur C++"
                )

    # --------------------------------------------------------
    # Rapport final
    # --------------------------------------------------------
    if verbose:
        print("\n" + "="*68)
        print("  RAPPORT BOUCLE FERMÉE OO ↔ OdM")
        print("="*68)
        print(f"  Cycles autorisés (D+=ALLOW) : {cycles_authorized}")
        print(f"  Cycles bloqués   (D+=BLOCK)  : {cycles_blocked}")
        print(f"  Actions exécutées            : {len(actions_executed)}")
        print(f"  Émergences ★                 : {len(emergences)}")
        for em in emergences:
            print(f"    {em}")
        print(f"  Expansions O-CPP HPC         : {len(hpc_expansions)}")
        for exp in hpc_expansions:
            print(
                f"    @ cycle {exp['cycle']} : "
                f"{exp['elements']} éléments → "
                f"{exp['valid_trajectories']} trajectoires"
            )
        print(f"\n  État final :")
        print(f"    Éléments     : {len(odm.elements)}")
        print(f"    Relations    : {len(odm.relations)}")
        print(f"    Organisations: {len(odm.organisations)}")

        # Connaissances retournées à OO
        print(f"\n  ★ CONNAISSANCES RETOURNÉES À OO :")
        if emergences:
            for em in emergences:
                print(f"    → {em.type.value} : {em.description}")
        else:
            print(f"    → (aucune émergence ce run)")
        print()

    return {
        "cycles_authorized":    cycles_authorized,
        "cycles_blocked":       cycles_blocked,
        "actions_executed":     len(actions_executed),
        "emergences_count":     len(emergences),
        "emergences":           [str(e) for e in emergences],
        "hpc_expansions":       hpc_expansions,
        "elements_final":       len(odm.elements),
        "relations_final":      len(odm.relations),
        "organisations_final":  len(odm.organisations),
    }


if __name__ == "__main__":
    run_experiment_004(n_cycles=15, hpc_check_every=5, verbose=True)
