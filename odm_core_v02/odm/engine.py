"""
OdM — Organique des Matières
Moteur principal : OdMCore v0.2

OdMCore est le système d'exécution de l'Organique des Matières.
Il maintient :
  - les éléments      (par id)
  - les relations     (par id)
  - les organisations (par id)
  - le journal d'événements (toutes les opérations, dans l'ordre)

Chaque opération :
  1. valide les règles (module operations.py)
  2. applique la transformation
  3. enregistre l'événement dans le journal

Les 7 opérations fondamentales :
  L  — LIAISON
  R  — RUPTURE
  T  — TRANSFORMATION
  C  — COMPOSITION
  CT — CONTENIR
  D  — DIVISION         (modes : partition | duplication | différenciation)
  K  — CARACTÉRISATION  (lecture seule)
"""

import copy
from typing import Any, Callable, Dict, List, Optional

from .element import Element
from .relation import Relation
from .organisation import Organisation
from .operations import Operations, RuleViolation


# ============================================================
# DIVISION — modes expérimentaux
# ============================================================

DIVISION_PARTITION      = "partition"
DIVISION_DUPLICATION    = "duplication"
DIVISION_DIFFERENCIATION = "différenciation"


# ============================================================
# MOTEUR ODM
# ============================================================

class OdMCore:
    """
    Moteur expérimental de l'Organique des Matières.

    Usage :
        odm = OdMCore()
        A = odm.add_element("A", CIRCLE, {"energie": 10})
        B = odm.add_element("B", TRIANGLE, {"matiere": 20})
        odm.liaison("A", "B")
        odm.caracterisation("A")
        odm.inspect()
    """

    def __init__(self):
        self.elements:      Dict[str, Element]      = {}
        self.relations:     Dict[str, Relation]     = {}
        self.organisations: Dict[str, Organisation] = {}

        self.event_log: List[Dict[str, Any]] = []

        self._relation_counter     = 0
        self._organisation_counter = 0
        self._time                 = 0   # horloge interne (cycle)

    # ============================================================
    # CRÉATION
    # ============================================================

    def add_element(
        self,
        element_id: str,
        form: str,
        content: Any
    ) -> Element:
        """Crée et enregistre un nouvel élément."""

        element = Element(
            id=element_id,
            form=form,
            content=content
        )

        self.elements[element_id] = element
        self._record("CREATION", [element_id])

        return element

    # ============================================================
    # 1 — LIAISON  L(A, B)
    # ============================================================

    def liaison(self, a_id: str, b_id: str) -> Relation:
        """
        Établit une relation active entre A et B.

        R1 : les deux éléments doivent exister et être distincts.
        """
        Operations.check_liaison(self.elements, a_id, b_id)

        self._relation_counter += 1
        relation_id = f"R{self._relation_counter}"

        relation = Relation(
            id=relation_id,
            source=a_id,
            target=b_id
        )

        self.relations[relation_id] = relation
        self.elements[a_id].relations.append(relation_id)
        self.elements[b_id].relations.append(relation_id)

        self._record("LIAISON", [a_id, b_id], result=relation_id)

        return relation

    # ============================================================
    # 2 — RUPTURE  R(Rn)
    # ============================================================

    def rupture(self, relation_id: str) -> Relation:
        """
        Rompt une relation active.

        R2 : la relation doit exister et être active.
        """
        Operations.check_rupture(self.relations, relation_id)

        relation = self.relations[relation_id]
        relation.active = False

        self._record(
            "RUPTURE",
            [relation.source, relation.target],
            result=relation_id
        )

        return relation

    # ============================================================
    # 3 — TRANSFORMATION  T(E, X)
    # ============================================================

    def transformation(
        self,
        element_id: str,
        *,
        content=None,
        state: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        capacities: Optional[Dict] = None
    ) -> Element:
        """
        Modifie un ou plusieurs aspects d'un élément.
        Conserve l'état avant dans l'historique de l'élément.

        R3 : au moins une caractéristique doit changer.
        """
        Operations.check_transformation(
            self.elements, element_id,
            content, state, properties, capacities
        )

        element = self.elements[element_id]
        before  = element.snapshot()

        if content is not None:
            element.content = content
        if state is not None:
            element.state.update(state)
        if properties is not None:
            element.properties.update(properties)
        if capacities is not None:
            element.capacities.update(capacities)

        after = element.snapshot()

        element.history.append({
            "operation": "TRANSFORMATION",
            "before":    before,
            "after":     after,
            "t":         self._time,
        })

        self._record("TRANSFORMATION", [element_id])

        return element

    # ============================================================
    # 4 — COMPOSITION  C(E₁, E₂, …, Eₙ) → O
    # ============================================================

    def composition(
        self,
        element_ids: List[str]
    ) -> Organisation:
        """
        Regroupe plusieurs éléments en une Organisation.

        R4 : ≥ 2 éléments distincts existants.
        """
        Operations.check_composition(self.elements, element_ids)

        self._organisation_counter += 1
        organisation_id = f"O{self._organisation_counter}"

        organisation = Organisation(
            id=organisation_id,
            elements=list(element_ids)
        )

        self.organisations[organisation_id] = organisation

        self._record(
            "COMPOSITION",
            list(element_ids),
            result=organisation_id
        )

        return organisation

    # ============================================================
    # 5 — CONTENIR  CT(A, B)
    # ============================================================

    def contenir(
        self,
        container_id: str,
        element_id: str
    ) -> Element:
        """
        Inscrit B à l'intérieur de l'état de A.

        R5 : contenant et contenu doivent exister et être distincts.
        """
        Operations.check_contenir(
            self.elements, container_id, element_id
        )

        container = self.elements[container_id]
        container.state.setdefault("contains", [])
        container.state["contains"].append(element_id)

        self._record("CONTENIR", [container_id, element_id])

        return container

    # ============================================================
    # 6 — DIVISION  D(A) → {A₁, A₂, …}
    # ============================================================

    def division(
        self,
        element_id: str,
        new_ids: List[str],
        mode: str = DIVISION_PARTITION,
        differenciation_fn: Optional[Callable] = None
    ) -> List[Element]:
        """
        Divise un élément en plusieurs éléments fils.

        Modes expérimentaux :
          - partition       : le contenu est distribué équitablement
          - duplication     : chaque fils reçoit une copie complète
          - différenciation : chaque fils est transformé via differenciation_fn

        R6 : ≥ 2 nouveaux identifiants, tous inexistants.
        """
        Operations.check_division(self.elements, element_id, new_ids)

        original = self.elements[element_id]
        children = []
        n        = len(new_ids)

        for i, new_id in enumerate(new_ids):

            # --- détermination du contenu fils ---
            if mode == DIVISION_PARTITION:
                raw = original.content
                if isinstance(raw, dict):
                    keys   = list(raw.keys())
                    chunk  = max(1, len(keys) // n)
                    start  = i * chunk
                    end    = start + chunk if i < n - 1 else len(keys)
                    child_content = {k: raw[k] for k in keys[start:end]}
                elif isinstance(raw, (list, tuple)):
                    chunk  = max(1, len(raw) // n)
                    start  = i * chunk
                    end    = start + chunk if i < n - 1 else len(raw)
                    child_content = type(raw)(raw[start:end])
                else:
                    child_content = copy.deepcopy(raw)

            elif mode == DIVISION_DUPLICATION:
                child_content = copy.deepcopy(original.content)

            elif mode == DIVISION_DIFFERENCIATION:
                if differenciation_fn is None:
                    raise RuleViolation(
                        "R6 — DIVISION/différenciation : "
                        "differenciation_fn est obligatoire dans ce mode."
                    )
                child_content = differenciation_fn(
                    copy.deepcopy(original.content), i
                )

            else:
                raise RuleViolation(
                    f"R6 — DIVISION : mode inconnu '{mode}'."
                )

            child = Element(
                id=new_id,
                form=original.form,
                content=child_content,
                state=copy.deepcopy(original.state),
                properties=copy.deepcopy(original.properties),
                capacities=copy.deepcopy(original.capacities),
            )

            self.elements[new_id] = child
            children.append(child)

        # Marque l'original comme divisé
        original.state["divided"]  = True
        original.state["children"] = new_ids

        self._record(
            "DIVISION",
            [element_id],
            result={"mode": mode, "children": new_ids}
        )

        return children

    # ============================================================
    # 7 — CARACTÉRISATION  K(E) → snapshot
    # ============================================================

    def caracterisation(self, element_id: str) -> Dict[str, Any]:
        """
        Retourne l'instantané complet de l'élément (lecture seule).

        R7 : ne modifie pas la cible.
        """
        Operations.check_caracterisation(self.elements, element_id)

        snapshot = self.elements[element_id].snapshot()

        self._record("CARACTÉRISATION", [element_id])

        return snapshot

    # ============================================================
    # JOURNAL INTERNE
    # ============================================================

    def _record(
        self,
        operation: str,
        targets: List[str],
        result: Any = None
    ) -> None:
        """Enregistre un événement dans le journal."""

        self._time += 1

        self.event_log.append({
            "t":         self._time,
            "operation": operation,
            "targets":   targets,
            "result":    result,
        })

    # ============================================================
    # AFFICHAGE
    # ============================================================

    def inspect(self) -> None:
        """Affiche l'état complet du système."""

        print("\n========== ODM ==========")

        print("\nÉLÉMENTS:")
        for e in self.elements.values():
            print(f"  {e}")

        print("\nRELATIONS:")
        for r in self.relations.values():
            print(f"  {r}")

        print("\nORGANISATIONS:")
        for o in self.organisations.values():
            print(f"  {o}")

        print("\nJOURNAL:")
        for event in self.event_log:
            result_str = (
                f" → {event['result']}" if event["result"] is not None else ""
            )
            print(
                f"  t{event['t']:03d}  {event['operation']}"
                f"({', '.join(str(x) for x in event['targets'])})"
                f"{result_str}"
            )

        print("\n=========================\n")

    # ============================================================
    # POSSIBILITÉS (première esquisse — Expérience 002)
    # ============================================================

    def possibilites(self, element_id: str) -> Dict[str, Any]:
        """
        Retourne les opérations actuellement réalisables sur un élément.
        C'est une première esquisse du système de possibilités OdM.
        """
        Operations.check_caracterisation(self.elements, element_id)

        element = self.elements[element_id]
        poss = {}

        # Peut-il être lié à d'autres éléments ?
        autres = [
            eid for eid in self.elements
            if eid != element_id
        ]
        poss["LIAISON_possible_avec"] = autres

        # Peut-il être transformé ?
        poss["TRANSFORMATION_possible"] = True

        # A-t-il des relations rompables ?
        actives = [
            rid for rid in element.relations
            if rid in self.relations and self.relations[rid].active
        ]
        poss["RUPTURE_possible"] = actives

        # Peut-il être divisé ?
        divided = element.state.get("divided", False)
        poss["DIVISION_possible"] = not divided

        # Peut-il contenir ?
        poss["CONTENIR_possible"] = [
            eid for eid in self.elements
            if eid != element_id
        ]

        # Peut-il faire partie d'une composition ?
        poss["COMPOSITION_possible"] = len(self.elements) >= 2

        return poss

    @property
    def cycle(self) -> int:
        return self._time

    def to_dict(self) -> Dict[str, Any]:
        """Exporte l'état complet du système sous forme sérialisable."""
        return {
            "elements": {eid: e.snapshot() for eid, e in self.elements.items()},
            "relations": [f"{r.source}_{r.target}" for r in self.relations.values() if r.active],
            "organisations": [o.id for o in self.organisations.values()],
            "time": self._time
        }
