"""
OdM — Organique des Matières
rules.py : Moteur de règles expérimental

Responsabilités :
  1. Calculer les opérations possibles depuis l'état actuel de OdMCore
  2. Sélectionner une opération selon une stratégie
  3. Détecter les émergences (★) dans un état
  4. Classifier l'émergence détectée

Stratégies de sélection disponibles :
  RANDOM       — sélection aléatoire parmi les possibles
  MAX_ENTROPY  — maximise l'entropie de l'état suivant
  SEQUENTIAL   — L→R→T→C→CT→D→K dans l'ordre
"""

import copy
import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .element import CIRCLE, TRIANGLE, SQUARE, STAR


# ============================================================
# ÉMERGENCE
# ============================================================

class EmergenceType(Enum):
    NOUVELLE_FORME      = "NOUVELLE_FORME"
    NOUVEAU_BLOC        = "NOUVEAU_BLOC"
    NOUVELLE_ORGANISATION = "NOUVELLE_ORGANISATION"
    NOUVELLE_CAPACITE   = "NOUVELLE_CAPACITE"
    TRANSFORMATION_CONNUE = "TRANSFORMATION_CONNUE"


@dataclass
class Emergence:
    """Une émergence ★ détectée lors d'un cycle."""
    type: EmergenceType
    description: str
    trigger_operation: str
    trigger_targets: List[str]
    cycle: int
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return (
            f"★ [{self.type.value}] @ t={self.cycle} "
            f"via {self.trigger_operation}({', '.join(self.trigger_targets)}) "
            f"— {self.description}"
        )


# ============================================================
# ACTION POSSIBLE
# ============================================================

@dataclass
class PossibleAction:
    """Une opération réalisable sur l'état actuel."""
    operation: str      # ex: "LIAISON", "DIVISION", ...
    targets: List[str]  # ex: ["A", "B"]
    kwargs: Dict[str, Any] = field(default_factory=dict)  # paramètres additionels

    def __str__(self):
        kwstr = (
            " " + " ".join(f"{k}={v}" for k, v in self.kwargs.items())
            if self.kwargs else ""
        )
        return f"{self.operation}({', '.join(self.targets)}){kwstr}"


# ============================================================
# MOTEUR DE RÈGLES
# ============================================================

class RulesEngine:
    """
    Calcule les possibilités, sélectionne une action, détecte les émergences.
    """

    STRATEGY_RANDOM     = "RANDOM"
    STRATEGY_MAX_ENTROPY = "MAX_ENTROPY"
    STRATEGY_SEQUENTIAL = "SEQUENTIAL"

    def __init__(self, strategy: str = STRATEGY_RANDOM, seed: Optional[int] = None):
        self.strategy = strategy
        self._rng = random.Random(seed)
        self._seen_signatures: set = set()   # signatures d'états déjà observés
        self._seen_topologies: set = set()   # topologies de relations déjà vues
        self._seq_index = 0                   # pour SEQUENTIAL

    # --------------------------------------------------------
    # 1. CALCUL DES POSSIBILITÉS
    # --------------------------------------------------------

    def compute_actions(self, odm) -> List[PossibleAction]:
        """
        Retourne toutes les PossibleAction réalisables sur l'état actuel d'OdMCore.
        """
        actions = []
        elements = odm.elements
        relations = odm.relations

        non_divided = [
            eid for eid, e in elements.items()
            if not e.state.get("divided", False)
        ]
        active_relations = [
            rid for rid, r in relations.items() if r.active
        ]
        all_ids = list(elements.keys())

        # --- LIAISON : tout couple distinct non encore lié ---
        already_linked = set()
        for r in relations.values():
            if r.active:
                already_linked.add((r.source, r.target))
                already_linked.add((r.target, r.source))

        for i, a in enumerate(all_ids):
            for b in all_ids[i+1:]:
                if (a, b) not in already_linked:
                    actions.append(PossibleAction("LIAISON", [a, b]))

        # --- RUPTURE : toutes les liaisons actives ---
        for rid in active_relations:
            actions.append(PossibleAction("RUPTURE", [rid]))

        # --- TRANSFORMATION : tous les éléments ---
        for eid in all_ids:
            e = elements[eid]
            # Transformation énergétique réaliste selon la forme
            if e.form == CIRCLE:
                new_content = copy.deepcopy(e.content)
                if isinstance(new_content, dict) and "energie" in new_content:
                    new_content["energie"] = int(new_content["energie"] * 1.5)
                    actions.append(PossibleAction(
                        "TRANSFORMATION", [eid],
                        {"content": new_content}
                    ))
            elif e.form == TRIANGLE:
                new_state = {"direction": "active"}
                actions.append(PossibleAction(
                    "TRANSFORMATION", [eid],
                    {"state": new_state}
                ))
            elif e.form == SQUARE:
                new_props = {"stabilite": "renforcee"}
                actions.append(PossibleAction(
                    "TRANSFORMATION", [eid],
                    {"properties": new_props}
                ))

        # --- COMPOSITION : tout triplet d'éléments (si ≥ 2 existent) ---
        if len(all_ids) >= 2:
            # On ne génère que les paires/triplets pour rester tractable
            for i, a in enumerate(all_ids):
                for b in all_ids[i+1:]:
                    actions.append(PossibleAction("COMPOSITION", [a, b]))

        # --- CONTENIR : tout couple distinct ---
        for a in all_ids:
            for b in all_ids:
                if a != b:
                    contained = elements[a].state.get("contains", [])
                    if b not in contained:
                        actions.append(PossibleAction("CONTENIR", [a, b]))

        # --- DIVISION : éléments non encore divisés ---
        for eid in non_divided:
            # Mode partition uniquement (pour garder les ids déterministes)
            actions.append(PossibleAction(
                "DIVISION", [eid],
                {"mode": "partition", "new_ids": [f"{eid}1", f"{eid}2"]}
            ))

        # --- CARACTÉRISATION : tous les éléments ---
        for eid in all_ids:
            actions.append(PossibleAction("CARACTÉRISATION", [eid]))

        return actions

    # --------------------------------------------------------
    # 2. SÉLECTION D'UNE ACTION
    # --------------------------------------------------------

    def select_action(
        self,
        actions: List[PossibleAction],
        odm=None
    ) -> Optional[PossibleAction]:
        """
        Choisit une action parmi les possibles selon la stratégie configurée.
        Retourne None si aucune action disponible.
        """
        if not actions:
            return None

        if self.strategy == self.STRATEGY_RANDOM:
            return self._rng.choice(actions)

        elif self.strategy == self.STRATEGY_SEQUENTIAL:
            ops_order = [
                "LIAISON", "RUPTURE", "TRANSFORMATION",
                "COMPOSITION", "CONTENIR", "DIVISION", "CARACTÉRISATION"
            ]
            target_op = ops_order[self._seq_index % len(ops_order)]
            self._seq_index += 1
            candidates = [a for a in actions if a.operation == target_op]
            if candidates:
                return self._rng.choice(candidates)
            return self._rng.choice(actions)

        elif self.strategy == self.STRATEGY_MAX_ENTROPY:
            return self._select_max_entropy(actions, odm)

        return self._rng.choice(actions)

    def _select_max_entropy(
        self,
        actions: List[PossibleAction],
        odm
    ) -> Optional[PossibleAction]:
        """
        Heuristique : préfère l'action qui diversifie le plus l'état.
        Priorise dans l'ordre : DIVISION > COMPOSITION > LIAISON > reste.
        """
        priority = {
            "DIVISION": 6,
            "COMPOSITION": 5,
            "LIAISON": 4,
            "TRANSFORMATION": 3,
            "CONTENIR": 2,
            "RUPTURE": 1,
            "CARACTÉRISATION": 0,
        }
        return max(actions, key=lambda a: priority.get(a.operation, 0))

    # --------------------------------------------------------
    # 3. EXÉCUTION D'UNE ACTION
    # --------------------------------------------------------

    def execute_action(self, odm, action: PossibleAction) -> Any:
        """
        Exécute une PossibleAction sur OdMCore et retourne le résultat.
        """
        op = action.operation
        targets = action.targets
        kw = action.kwargs

        if op == "LIAISON":
            return odm.liaison(targets[0], targets[1])

        elif op == "RUPTURE":
            return odm.rupture(targets[0])

        elif op == "TRANSFORMATION":
            return odm.transformation(targets[0], **kw)

        elif op == "COMPOSITION":
            return odm.composition(targets)

        elif op == "CONTENIR":
            return odm.contenir(targets[0], targets[1])

        elif op == "DIVISION":
            new_ids = kw.get("new_ids", [f"{targets[0]}1", f"{targets[0]}2"])
            mode = kw.get("mode", "partition")
            # Assure l'unicité des ids
            base_ids = new_ids
            suffix = 0
            while any(nid in odm.elements for nid in base_ids):
                suffix += 1
                base_ids = [f"{nid}_{suffix}" for nid in new_ids]
            return odm.division(targets[0], base_ids, mode=mode)

        elif op == "CARACTÉRISATION":
            return odm.caracterisation(targets[0])

        raise ValueError(f"Opération inconnue : {op}")

    # --------------------------------------------------------
    # 4. DÉTECTION D'ÉMERGENCE
    # --------------------------------------------------------

    def detect_emergence(
        self,
        odm,
        last_action: PossibleAction,
        cycle: int
    ) -> Optional[Emergence]:
        """
        Analyse l'état courant d'OdMCore et détecte une émergence ★.
        """
        # Signature topologique : frozenset des relations actives
        topology = frozenset(
            (r.source, r.target)
            for r in odm.relations.values()
            if r.active
        )

        # Signature d'état global : formes + contenus
        state_sig = frozenset(
            (eid, e.form, _hash_content(e.content))
            for eid, e in odm.elements.items()
        )

        # Nouvelle topologie jamais vue ?
        if topology and topology not in self._seen_topologies and len(topology) > 1:
            self._seen_topologies.add(topology)
            return Emergence(
                type=EmergenceType.NOUVELLE_ORGANISATION,
                description=(
                    f"Topologie relationnelle inédite ({len(topology)} liens actifs)"
                ),
                trigger_operation=last_action.operation,
                trigger_targets=last_action.targets,
                cycle=cycle,
                details={"topology": list(topology)},
            )

        # Nouvel état global jamais vu ?
        if state_sig not in self._seen_signatures:
            self._seen_signatures.add(state_sig)
            # Vérifie si un élément possède une capacité nouvelle
            for eid, e in odm.elements.items():
                if e.capacities and any(
                    v for v in e.capacities.values()
                ):
                    return Emergence(
                        type=EmergenceType.NOUVELLE_CAPACITE,
                        description=(
                            f"L'élément '{eid}' a déverrouillé une capacité "
                            f"via {last_action.operation}"
                        ),
                        trigger_operation=last_action.operation,
                        trigger_targets=last_action.targets,
                        cycle=cycle,
                        details={"element": eid, "capacities": dict(e.capacities)},
                    )

        # Nouvelle forme ★ ?
        for eid, e in odm.elements.items():
            if e.form == STAR:
                return Emergence(
                    type=EmergenceType.NOUVELLE_FORME,
                    description=f"L'élément '{eid}' a la forme ★ (Émergence pure)",
                    trigger_operation=last_action.operation,
                    trigger_targets=last_action.targets,
                    cycle=cycle,
                    details={"element": eid},
                )

        # Élément divisé pour la première fois ?
        if last_action.operation == "DIVISION":
            return Emergence(
                type=EmergenceType.NOUVEAU_BLOC,
                description=(
                    f"L'élément '{last_action.targets[0]}' a produit des fils "
                    f"par division (mode: {last_action.kwargs.get('mode', '?')})"
                ),
                trigger_operation=last_action.operation,
                trigger_targets=last_action.targets,
                cycle=cycle,
            )

        return None  # Pas d'émergence ce cycle

    # --------------------------------------------------------
    # CLASSIFICATION D'ÉMERGENCE
    # --------------------------------------------------------

    def classify_emergence(self, emergence: Emergence) -> str:
        """
        Retourne une description lisible de la classification de l'émergence.
        """
        lines = [
            f"",
            f"  ★ ÉMERGENCE DÉTECTÉE (cycle {emergence.cycle})",
            f"  {'─'*48}",
            f"  Type       : {emergence.type.value}",
            f"  Déclenchée : {emergence.trigger_operation}"
            f"({', '.join(emergence.trigger_targets)})",
            f"  Description: {emergence.description}",
        ]
        if emergence.details:
            lines.append(f"  Détails    : {emergence.details}")
        lines.append("")
        lines.append("  Classification :")
        lines.append(
            f"  ├── Nouveau bloc          ? "
            + ("OUI" if emergence.type == EmergenceType.NOUVEAU_BLOC else "non")
        )
        lines.append(
            f"  ├── Nouvelle organisation ? "
            + ("OUI" if emergence.type == EmergenceType.NOUVELLE_ORGANISATION else "non")
        )
        lines.append(
            f"  ├── Nouvelle capacité     ? "
            + ("OUI" if emergence.type == EmergenceType.NOUVELLE_CAPACITE else "non")
        )
        lines.append(
            f"  ├── Nouvelle forme        ? "
            + ("OUI" if emergence.type == EmergenceType.NOUVELLE_FORME else "non")
        )
        lines.append(
            f"  └── Transformation connue ? "
            + ("OUI" if emergence.type == EmergenceType.TRANSFORMATION_CONNUE else "non")
        )
        return "\n".join(lines)


# ============================================================
# UTILITAIRES
# ============================================================

def _hash_content(content: Any) -> str:
    """Produit une signature stable d'un contenu pour comparaison."""
    try:
        if isinstance(content, dict):
            return str(sorted(content.items()))
        return str(content)
    except Exception:
        return repr(content)
