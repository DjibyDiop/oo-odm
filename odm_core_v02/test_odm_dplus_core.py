"""
OdM — Test d'Intégration Natif D+ : Expérience 006
=======================================================
Phase 4 — Option 2 : Le Moteur OdM Intégral en pur D+

Valide l'intégralité du chemin bout-en-bout :
  Python (MEO) → OIR EXECUTE_DPLUS_OP → OMXBridge → ODPlusEngine
  → odm_core.plus (dpc.exe compilé) → retour résultat natif D+

Les 7 opérations fondamentales (LIAISON, RUPTURE, TRANSFORMATION,
COMPOSITION, CONTENIR, DIVISION, CARACTÉRISATION) sont toutes exercées
via l'OIRType.EXECUTE_DPLUS_OP en passant par l'organe OdMCoreOrgan.

RÈGLE : Zéro Mocks — les graphes OPI (.graph) sont lus depuis les
fichiers compilés par dpc.exe uniquement.
"""

import sys
import os

# Chemin racine pour tous les imports
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from odm_core_v02.omx_bridge import OMXBridge
from omx.oir import OIRInstruction, OIRType


# =============================================================================
# DONNÉES DE RÉFÉRENCE : Les 4 Formes et leurs identifiants canoniques
# =============================================================================
FORME_CERCLE   = {"id": 1, "symbol": "○", "code": 1}
FORME_TRIANGLE = {"id": 2, "symbol": "△", "code": 2}
FORME_CARRE    = {"id": 3, "symbol": "□", "code": 3}
FORME_ETOILE   = {"id": 4, "symbol": "★", "code": 4}

ALL_FORMS = [FORME_CERCLE, FORME_TRIANGLE, FORME_CARRE, FORME_ETOILE]


# =============================================================================
# ORCHESTRATEUR DE TEST : Exercice direct de l'organe OdMCoreOrgan via OIR
# =============================================================================

def _execute_dplus_op(bridge: OMXBridge, operation: str, targets: list) -> dict:
    """
    Envoie une instruction EXECUTE_DPLUS_OP directement au moteur O-D+
    via l'OMXBridge, en court-circuitant la logique métier pour
    valider le chemin natif pur.
    """
    instr = OIRInstruction(
        OIRType.EXECUTE_DPLUS_OP,
        {
            "operation": operation,
            "targets": targets,
        }
    )
    return bridge._dplus.process(instr)


# =============================================================================
# SUITE DE TESTS : Les 7 Opérations Fondamentales via D+ Natif
# =============================================================================

def test_odm_dplus_core():
    print()
    print("=" * 65)
    print("  OdM EXP-006 : Moteur Cœur Natif D+ — Les 7 Opérations")
    print("=" * 65)

    bridge = OMXBridge(verbose=True)
    errors = []

    # ------------------------------------------------------------------
    # OP 1 — LIAISON : Connexion structurelle entre ○ et △
    # ------------------------------------------------------------------
    print("\n[OP 1/7] LIAISON ○ → △")
    res = _execute_dplus_op(bridge, "LIAISON", [FORME_CERCLE["id"], FORME_TRIANGLE["id"]])
    assert res.get("executed") is True, f"LIAISON failed: {res}"
    assert res.get("operation") == "LIAISON"
    assert res.get("atp_spent") == 10
    assert res.get("organ") == "OdMCoreOrgan"
    assert res.get("is_emergence") is False
    print(f"    ✓ LIAISON → atp_spent={res['atp_spent']}, organ={res['organ']}")

    # ------------------------------------------------------------------
    # OP 2 — RUPTURE : Clivage d'une liaison existante
    # ------------------------------------------------------------------
    print("\n[OP 2/7] RUPTURE (relation ○–△)")
    res = _execute_dplus_op(bridge, "RUPTURE", [1])
    assert res.get("executed") is True, f"RUPTURE failed: {res}"
    assert res.get("operation") == "RUPTURE"
    assert res.get("atp_spent") == 0
    assert res.get("is_emergence") is False
    print(f"    ✓ RUPTURE → atp_spent={res['atp_spent']} (opération sans coût énergétique)")

    # ------------------------------------------------------------------
    # OP 3 — TRANSFORMATION : Mutation énergétique d'un bloc □
    # ------------------------------------------------------------------
    print("\n[OP 3/7] TRANSFORMATION □ → ★")
    res = _execute_dplus_op(bridge, "TRANSFORMATION", [FORME_CARRE["id"]])
    assert res.get("executed") is True, f"TRANSFORMATION failed: {res}"
    assert res.get("operation") == "TRANSFORMATION"
    assert res.get("atp_spent") == 20
    assert res.get("organ") == "OdMCoreOrgan"
    print(f"    ✓ TRANSFORMATION → atp_spent={res['atp_spent']}")

    # ------------------------------------------------------------------
    # OP 4 — COMPOSITION : Formation d'une organisation (○ + △ + □)
    # ------------------------------------------------------------------
    print("\n[OP 4/7] COMPOSITION (○ + △ + □)")
    res = _execute_dplus_op(bridge, "COMPOSITION", [
        FORME_CERCLE["id"], FORME_TRIANGLE["id"], FORME_CARRE["id"]
    ])
    assert res.get("executed") is True, f"COMPOSITION failed: {res}"
    assert res.get("operation") == "COMPOSITION"
    assert res.get("atp_spent") == 15
    assert res.get("is_emergence") is False
    print(f"    ✓ COMPOSITION → atp_spent={res['atp_spent']}, targets={res.get('targets')}")

    # ------------------------------------------------------------------
    # OP 5 — CONTENIR : Inclusion de □ dans ○
    # ------------------------------------------------------------------
    print("\n[OP 5/7] CONTENIR (□ ⊂ ○)")
    res = _execute_dplus_op(bridge, "CONTENIR", [FORME_CARRE["id"], FORME_CERCLE["id"]])
    assert res.get("executed") is True, f"CONTENIR failed: {res}"
    assert res.get("operation") == "CONTENIR"
    assert res.get("atp_spent") == 5
    print(f"    ✓ CONTENIR → atp_spent={res['atp_spent']}")

    # ------------------------------------------------------------------
    # OP 6 — DIVISION : Scission et émergence de ★ (singularité)
    # ------------------------------------------------------------------
    print("\n[OP 6/7] DIVISION ★ (émergence cellulaire)")
    res = _execute_dplus_op(bridge, "DIVISION", [FORME_ETOILE["id"]])
    assert res.get("executed") is True, f"DIVISION failed: {res}"
    assert res.get("operation") == "DIVISION"
    assert res.get("atp_spent") == 30
    assert res.get("is_emergence") is True, "DIVISION doit provoquer une émergence ★"
    assert res.get("organ") == "OdMCoreOrgan"
    print(f"    ✓ DIVISION → atp_spent={res['atp_spent']}, is_emergence={res['is_emergence']} ★")

    # ------------------------------------------------------------------
    # OP 7 — CARACTÉRISATION : Snapshot d'observation pure
    # ------------------------------------------------------------------
    print("\n[OP 7/7] CARACTÉRISATION (observation ★)")
    res = _execute_dplus_op(bridge, "CARACTÉRISATION", [FORME_ETOILE["id"]])
    assert res.get("executed") is True, f"CARACTÉRISATION failed: {res}"
    assert res.get("operation") == "CARACTÉRISATION"
    assert res.get("atp_spent") == 0
    assert res.get("is_emergence") is False
    print(f"    ✓ CARACTÉRISATION → atp_spent={res['atp_spent']} (observation sans coût)")

    # ------------------------------------------------------------------
    # VÉRIFICATION GLOBALE : Intégrité du graphe OdMCoreOrgan
    # ------------------------------------------------------------------
    print("\n[VÉRIFICATION] Intégrité structurelle de l'organe OdMCoreOrgan")
    import json
    dplus_dir = os.path.join(_ROOT, "dplus")
    core_graph_path = os.path.join(dplus_dir, "odm_core.graph")
    assert os.path.exists(core_graph_path), f"Graphe OPI absent : {core_graph_path}"

    with open(core_graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)

    node_labels = [n["label"] for n in graph.get("nodes", [])]

    # Les 7 signaux fondamentaux doivent être présents dans le graphe compilé
    expected_signals = [
        "LiaisonSignal", "RuptureSignal", "TransformationSignal",
        "CompositionSignal", "ContenirSignal", "DivisionSignal",
        "CaracterisationSignal",
    ]
    for sig in expected_signals:
        assert sig in node_labels, f"Signal manquant dans odm_core.graph : {sig}"

    # Les 2 tissus génomiques doivent être présents
    assert "odm_engine" in node_labels, "Cellule odm_engine manquante dans odm_core.graph"
    assert "discovery_watcher" in node_labels, "Cellule discovery_watcher manquante dans odm_core.graph"

    print(f"    ✓ {len(expected_signals)} signaux fondamentaux présents")
    print(f"    ✓ 2 cellules génomiques (odm_engine, discovery_watcher) présentes")
    print(f"    ✓ {len(node_labels)} nœuds OPI au total dans odm_core.graph")

    # ------------------------------------------------------------------
    # RAPPORT FINAL
    # ------------------------------------------------------------------
    print()
    print("=" * 65)
    print("  OdM EXP-006 : ✅ LES 7 OPÉRATIONS FONDAMENTALES VALIDÉES")
    print("  Moteur Cœur Natif D+ (odm_core.plus) — Chemin bout-en-bout")
    print("  OIR EXECUTE_DPLUS_OP → OMXBridge → ODPlusEngine → OdMCoreOrgan")
    print("=" * 65)


# =============================================================================
# POINT D'ENTRÉE STANDALONE
# =============================================================================

if __name__ == "__main__":
    try:
        test_odm_dplus_core()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[ÉCHEC] Assertion : {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n[ERREUR FATALE] {e}")
        traceback.print_exc()
        sys.exit(2)
