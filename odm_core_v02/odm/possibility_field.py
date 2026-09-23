"""
OdM — Possibility Field (Organisme de Possibilités)
Vision ultime du plan.md (lignes 14548-14665) :

L'Organisme de Possibilités maintient une représentation dynamique et vivante de :
  1. Ce qui existe       (elements, relations, organisations)
  2. Ce qui est possible   (espace combinatoire atteignable calculé en temps réel)
  3. Ce qui a été essayé   (historique des trajectoires et états explorés)
  4. Ce qui a émergé       (singularités ★ classifiées)
  5. Ce qui est interdit   (verdicts FORBID D+, incompatibilités ontologiques)
  6. Ce qui reste inexploré (front de découverte, ratio d'inconnu)

Évolution :
  P₀ ──(expérience)──► P₁ ──(émergence)──► P₂ ──(organisation)──► P₃ ...
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import copy
import math

from .element import Element
from .relation import Relation
from .organisation import Organisation
from .engine import OdMCore
from .rules import RulesEngine, PossibleAction, Emergence, EmergenceType


@dataclass
class FieldSnapshot:
    """Instantané d'un état du champ des possibilités P_k."""
    generation: int
    element_count: int
    relation_count: int
    organisation_count: int
    possible_actions_count: int
    explored_trajectories_count: int
    emergences_count: int
    forbidden_count: int
    unexplored_ratio: float
    entropy: float
    description: str = ""


class PossibilityField:
    """
    L'Organisme de Possibilités (Possibility Field).
    Instrument scientifique vivant couplé à OO.
    """

    def __init__(self, core: Optional[OdMCore] = None, bridge: Any = None, seed: Optional[int] = None):
        self.core: OdMCore = core if core is not None else OdMCore()
        self.bridge: Any = bridge
        self.rules: RulesEngine = RulesEngine(strategy=RulesEngine.STRATEGY_RANDOM, seed=seed)

        self.generation: int = 0
        self.history: List[FieldSnapshot] = []

        # --- Les 6 Compartiments Fondamentaux ---
        # 1. Ce qui existe
        self.existing: Dict[str, Any] = {
            "elements": {},
            "relations": {},
            "organisations": {}
        }

        # 2. Ce qui est possible (front immédiat)
        self.possibilities: List[PossibleAction] = []

        # 3. Ce qui a déjà été essayé (signatures de trajectoires)
        self.explored_trajectories: List[Dict[str, Any]] = []
        self._explored_signatures: Set[str] = set()

        # 4. Ce qui a émergé (singularités ★)
        self.emergences: List[Emergence] = []

        # 5. Ce qui est interdit / impossible
        self.forbidden_actions: List[Dict[str, Any]] = []

        # 6. Ce qui reste inexploré (branches frontières recensées)
        self.unexplored_front: List[str] = []

        # Métriques informationnelles
        self.current_entropy: float = 0.0
        self.unexplored_ratio: float = 100.0
        self.is_saturated: bool = False

        # Initialisation du champ initial P0
        self._refresh_existing()
        self._compute_current_possibilities()
        self._record_snapshot("P0 — Initialisation du Champ des Possibilités")

    # --------------------------------------------------------
    # SYNCHRONISATION DU COMPARTIMENT "EXISTANT"
    # --------------------------------------------------------

    def _refresh_existing(self):
        """Met à jour l'inventaire de ce qui existe réellement dans l'espace OdM."""
        self.existing["elements"] = {
            eid: el.snapshot() for eid, el in self.core.elements.items()
        }
        self.existing["relations"] = {
            rid: {"source": r.source, "target": r.target, "active": r.active}
            for rid, r in self.core.relations.items()
        }
        self.existing["organisations"] = {
            oid: {"elements": list(o.elements), "relations": list(o.relations)}
            for oid, o in self.core.organisations.items()
        }

    # --------------------------------------------------------
    # CALCUL DU COMPARTIMENT "POSSIBLES" & "INEXPLORÉ"
    # --------------------------------------------------------

    def _compute_current_possibilities(self):
        """Calcule les actions possibles et actualise le front inexploré."""
        self.possibilities = self.rules.compute_actions(self.core)

        # Génération des signatures de ce qui est désormais possible
        for prop in self.possibilities:
            sig = str(prop)
            if sig not in self._explored_signatures and sig not in self.unexplored_front:
                self.unexplored_front.append(sig)

        # Calcul du ratio d'inconnu (estimé)
        total_seen = len(self._explored_signatures) + len(self.unexplored_front)
        if total_seen > 0:
            self.unexplored_ratio = round((len(self.unexplored_front) / total_seen) * 100.0, 2)
        else:
            self.unexplored_ratio = 100.0

        # Calcul d'entropie informationnelle des possibilités (distribution des types d'opérations)
        op_counts = {}
        for p in self.possibilities:
            op_counts[p.operation] = op_counts.get(p.operation, 0) + 1

        total_ops = len(self.possibilities)
        if total_ops > 0:
            ent = 0.0
            for count in op_counts.values():
                prob = count / total_ops
                ent -= prob * math.log2(prob)
            self.current_entropy = round(ent, 3)
        else:
            self.current_entropy = 0.0

    # --------------------------------------------------------
    # TRANSITION ÉVOLUTIVE : P_k → P_{k+1}
    # --------------------------------------------------------

    def evolve_step(
        self,
        chosen_action: Optional[PossibleAction] = None,
        strategy: str = "AUTO"
    ) -> Dict[str, Any]:
        """
        Effectue une transition dynamique dans le Champ des Possibilités :
          1. Sélectionne ou reçoit une action
          2. Consulte D+ via le pont OMX (SandBox & Ontologie)
          3. Si refusé (FORBID) : enregistre dans 'forbidden'
          4. Si autorisé (ALLOW) : exécute sur OdMCore
          5. Détecte les émergences ★
          6. Met à jour P_k -> P_{k+1}
        """
        self._compute_current_possibilities()

        if not self.possibilities:
            return {
                "status": "STAGNATION",
                "reason": "Aucune action possible dans l'espace actuel",
                "generation": self.generation
            }

        # Sélection de l'action si non fournie
        action = chosen_action
        if action is None:
            if strategy in ["RANDOM", "AUTO"]:
                action = self.rules.select_action(self.possibilities, self.core)
            else:
                action = self.possibilities[0]

        action_desc = str(action)

        # 1. Consultation de la Constitution et Ontologie D+
        is_allowed = True
        judge_verdict = "ALLOW"

        if self.bridge is not None:
            try:
                # Interrogation via le pont OMX
                is_allowed = self.bridge.authorize_cycle(
                    cycle=self.generation + 1,
                    elements=self.core.elements,
                    scope="SANDBOX"
                )
                judge_verdict = "ALLOW" if is_allowed else "FORBID"
            except Exception as e:
                is_allowed = False
                judge_verdict = f"FORBID_ERR({e})"

        # 2. Si D+ interdit : enregistrement dans 'forbidden'
        if not is_allowed:
            forbidden_record = {
                "generation": self.generation,
                "action": action_desc,
                "operation": action.operation,
                "reason": f"Rejet constitutionnel D+ ({judge_verdict})",
            }
            self.forbidden_actions.append(forbidden_record)
            return {
                "status": "BLOCKED",
                "action": action_desc,
                "verdict": judge_verdict,
                "generation": self.generation
            }

        # 3. Exécution de l'action autorisée
        res_exec = self.rules.execute_action(self.core, action)

        # Détection d'émergence
        emergence = self.rules.detect_emergence(
            self.core,
            last_action=action,
            cycle=self.generation + 1
        )

        # Enregistrement dans les trajectoires explorées
        sig = action_desc
        self._explored_signatures.add(sig)
        if sig in self.unexplored_front:
            self.unexplored_front.remove(sig)

        trajectory_entry = {
            "generation": self.generation + 1,
            "action": action_desc,
            "operation": action.operation,
            "targets": action.targets,
            "kwargs": action.kwargs,
            "has_emergence": emergence is not None
        }
        self.explored_trajectories.append(trajectory_entry)

        # 4. Traitement des émergences ★
        if emergence:
            self.emergences.append(emergence)

        # 5. Incrémentation de la génération P_k → P_{k+1}
        self.generation += 1
        self._refresh_existing()
        self._compute_current_possibilities()

        # Notification D+ de la trajectoire (si pont disponible)
        if self.bridge is not None and hasattr(self.bridge, "record_trajectory_dplus"):
            self.bridge.record_trajectory_dplus(
                trajectory_id=self.generation,
                terminal_nodes=len(self.core.elements),
                has_singularity=emergence is not None
            )

        # Vérification du seuil de saturation (100 trajectoires comme dans odm_possibilities.plus)
        if len(self.explored_trajectories) >= 100:
            self.is_saturated = True

        desc = f"P{self.generation} — via {action.operation} ({'★ Émergence' if emergence else 'Normal'})"
        snapshot = self._record_snapshot(desc)

        return {
            "status": "EVOLVED",
            "generation": self.generation,
            "action": action_desc,
            "emergence": emergence,
            "snapshot": snapshot
        }

    # --------------------------------------------------------
    # HISTORIQUE ET SNAPSHOTS DU CHAMP
    # --------------------------------------------------------

    def _record_snapshot(self, description: str = "") -> FieldSnapshot:
        """Enregistre un snapshot de l'état actuel du champ des possibilités."""
        snap = FieldSnapshot(
            generation=self.generation,
            element_count=len(self.core.elements),
            relation_count=len(self.core.relations),
            organisation_count=len(self.core.organisations),
            possible_actions_count=len(self.possibilities),
            explored_trajectories_count=len(self.explored_trajectories),
            emergences_count=len(self.emergences),
            forbidden_count=len(self.forbidden_actions),
            unexplored_ratio=self.unexplored_ratio,
            entropy=self.current_entropy,
            description=description
        )
        self.history.append(snap)
        return snap

    # --------------------------------------------------------
    # RESTITUTION DU RAPPORT SCIENTIFIQUE POUR OO
    # --------------------------------------------------------

    def export_scientific_report(self) -> Dict[str, Any]:
        """
        Génère le rapport complet de l'Organisme de Possibilités pour restitution à OO :
          - État courant P_k
          - Synthèse des 6 compartiments
          - Singularités et découvertes
          - Espace inexploré restant
        """
        return {
            "field_generation": self.generation,
            "dimensions": {
                "existing_elements": len(self.core.elements),
                "active_relations": len([r for r in self.core.relations.values() if r.active]),
                "organisations": len(self.core.organisations),
                "possibilities_open": len(self.possibilities),
                "explored_trajectories": len(self.explored_trajectories),
                "discovered_emergences": len(self.emergences),
                "forbidden_actions": len(self.forbidden_actions),
                "unexplored_branches": len(self.unexplored_front),
            },
            "metrics": {
                "field_entropy": self.current_entropy,
                "unexplored_ratio_pct": self.unexplored_ratio,
                "is_saturated": self.is_saturated,
            },
            "emergences_detail": [
                {
                    "type": em.type.value if hasattr(em.type, "value") else str(em.type),
                    "cycle": em.cycle,
                    "action": f"{em.trigger_operation}({', '.join(em.trigger_targets)})",
                    "description": em.description,
                }
                for em in self.emergences
            ],
            "forbidden_detail": list(self.forbidden_actions),
            "evolution_timeline": [
                {
                    "gen": s.generation,
                    "elements": s.element_count,
                    "possibilities": s.possible_actions_count,
                    "emergences": s.emergences_count,
                    "entropy": s.entropy,
                    "desc": s.description
                }
                for s in self.history
            ]
        }
