"""
OdM — Expérience 001 (Canonique plan.md)
Séquence : L(A,B) → T(A) → C(A,B,C) → CT(A,C) → D(B,partition) → K(A) → R(R1)

Éléments initiaux :
   ○A = {energie: 10}
   △B = {matiere: 20}
   □C = {limite: 30}

Le moteur enregistre l'état complet à chaque étape.
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# Ajout du chemin racine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from odm_core_v02.odm.engine import OdMCore, DIVISION_PARTITION
from odm_core_v02.odm.element import CIRCLE, TRIANGLE, SQUARE


def run_experiment_001(verbose: bool = True) -> dict:
    """
    Exécute l'expérience 001 canonique.
    Retourne un rapport structuré.
    """

    odm = OdMCore()

    def _banner(title):
        if verbose:
            print(f"\n{'='*52}")
            print(f"  {title}")
            print(f"{'='*52}")

    def _step(label):
        if verbose:
            print(f"\n--- {label} ---")
            _inspect_compact(odm)

    def _inspect_compact(core):
        for e in core.elements.values():
            print(f"  {e}")
        rels = [r for r in core.relations.values()]
        if rels:
            print("  Relations :")
            for r in rels:
                status = "active" if r.active else "rompue"
                print(f"    {r.id}: {r.source} → {r.target} [{status}]")
        orgs = list(core.organisations.values())
        if orgs:
            print("  Organisations :")
            for o in orgs:
                print(f"    {o.id}: {o.elements}")

    _banner("OdM — EXPÉRIENCE 001 (Séquence Canonique)")

    # --------------------------------------------------------
    # t0 : État initial
    # --------------------------------------------------------
    A = odm.add_element("A", CIRCLE,   {"energie": 10})
    B = odm.add_element("B", TRIANGLE, {"matiere": 20})
    C = odm.add_element("C", SQUARE,   {"limite":  30})
    _step("t0 — ÉTAT INITIAL")

    # --------------------------------------------------------
    # t1 : L(A, B)
    # --------------------------------------------------------
    r_ab = odm.liaison("A", "B")
    _step(f"t1 — LIAISON(A, B) → {r_ab.id}")

    # --------------------------------------------------------
    # t2 : T(A) — Transformation énergétique
    # --------------------------------------------------------
    odm.transformation("A", content={"energie": 25}, state={"temperature": 40})
    _step("t2 — TRANSFORMATION(A) : énergie 10→25, T°=40")

    # --------------------------------------------------------
    # t3 : C(A, B, C)
    # --------------------------------------------------------
    org = odm.composition(["A", "B", "C"])
    _step(f"t3 — COMPOSITION(A,B,C) → {org.id}")

    # --------------------------------------------------------
    # t4 : CT(A, C) — A contient C
    # --------------------------------------------------------
    odm.contenir("A", "C")
    _step("t4 — CONTENIR(A, C) : C est maintenant dans A")

    # --------------------------------------------------------
    # t5 : D(B, partition)
    # --------------------------------------------------------
    children = odm.division("B", ["B1", "B2"], mode=DIVISION_PARTITION)
    _step(f"t5 — DIVISION(B, partition) → {[c.id for c in children]}")

    # --------------------------------------------------------
    # t6 : K(A) — lecture seule
    # --------------------------------------------------------
    snap_a = odm.caracterisation("A")
    _step("t6 — CARACTÉRISATION(A)")
    if verbose:
        print(f"  Snapshot A :")
        for k, v in snap_a.items():
            print(f"    {k}: {v}")

    # --------------------------------------------------------
    # t7 : R(R1) — Rupture de la liaison A-B
    # --------------------------------------------------------
    odm.rupture("R1")
    _step("t7 — RUPTURE(R1) : lien A↔B rompu")

    # --------------------------------------------------------
    # Journal final
    # --------------------------------------------------------
    if verbose:
        _banner("JOURNAL COMPLET")
        for event in odm.event_log:
            res = f" → {event['result']}" if event["result"] is not None else ""
            print(
                f"  t{event['t']:03d}  {event['operation']}"
                f"({', '.join(str(x) for x in event['targets'])}){res}"
            )

    # --------------------------------------------------------
    # Rapport structuré
    # --------------------------------------------------------
    report = {
        "elements_count":      len(odm.elements),
        "relations_count":     len(odm.relations),
        "organisations_count": len(odm.organisations),
        "journal_length":      len(odm.event_log),
        "B_divided":           odm.elements["B"].state.get("divided", False),
        "B1_exists":           "B1" in odm.elements,
        "B2_exists":           "B2" in odm.elements,
        "R1_broken":           not odm.relations["R1"].active,
        "A_contains_C":        "C" in odm.elements["A"].state.get("contains", []),
        "snap_A_energie":      snap_a.get("content", {}).get("energie"),
        "organisation_ABC":    "O1" in odm.organisations,
    }

    if verbose:
        _banner("RÉSULTAT EXPÉRIENCE 001")
        for k, v in report.items():
            status = "✓" if v else "✗" if isinstance(v, bool) else "→"
            print(f"  {status} {k}: {v}")
        print()

    return report


if __name__ == "__main__":
    run_experiment_001(verbose=True)
