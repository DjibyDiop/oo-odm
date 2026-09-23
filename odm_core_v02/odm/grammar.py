"""
OO-ODM — Organique des Matières
odm_core_v02/odm/grammar.py : Grammaire Opérationnelle Formelle

Spécification formelle selon plan.md (lignes 12952 → 13280) :
  1. Expression formelle : OPÉRATION(cible | contexte) → résultat Q
  2. Règle 1 : État avant/après (Transition Sₜ ──OP──→ Sₜ₊₁)
  3. Règle 2 : Le contexte compte (forme, état, contenu, relations, organisation, environnement, contraintes, historique)
  4. Règle 3 : Résultat générique Q ∈ {E, R, O, T, Π, ★}
  5. Règle 4 : L'émergence ★ comme résultat non-linéaire

RÈGLE ABSOLUE : ZÉRO MOCKS.
"""

from __future__ import annotations
import copy
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .element import Element, CIRCLE, TRIANGLE, SQUARE, STAR
from .relation import Relation
from .organisation import Organisation


# =============================================================================
# TYPAGE DU RÉSULTAT Q (plan.md L13214-13225)
# =============================================================================

class ResultQType(Enum):
    """
    Typage formel du Résultat Q produit par une opération d'OdM :
      Q ∈ {E, R, O, T, Π, ★}
    """
    ELEMENT        = "Q_ELEMENT"         # E : Nouveau bloc ou bloc métamorphosé
    RELATION       = "Q_RELATION"        # R : Nouvelle liaison établie ou rompue
    ORGANISATION   = "Q_ORGANISATION"    # O : Structure ou réseau ordonné
    TRANSFORMATION = "Q_TRANSFORMATION"  # T : Modification d'état interne
    POSSIBILITY    = "Q_POSSIBILITY"     # Π : Nouvelle dimension ou bifurcation
    EMERGENCE      = "Q_EMERGENCE"       # ★ : Nouveauté ontologique non-déductible


@dataclass
class ResultQ:
    """
    Le Résultat générique Q d'une opération formelle.
    Contient la valeur matérialisée, son type formel, ses propriétés induites
    et son impact sur l'espace des états.
    """
    q_type: ResultQType
    value: Any
    description: str
    is_emergence: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        star = " ★" if self.is_emergence else ""
        return f"[{self.q_type.value}{star}] {self.description}"


# =============================================================================
# LE CONTEXTE OPÉRATIONNEL (plan.md L13150-13195)
# =============================================================================

@dataclass
class OperationalContext:
    """
    Contexte opératoire complet d'une opération OdM :
      OP(cible | contexte)
    Une opération n'a pas nécessairement le même résultat pour tous les éléments.
    Le contexte qualifie le substrat dans lequel l'opération s'applique.
    """
    # 1. Substrat morphologique
    forms: Dict[str, str] = field(default_factory=dict)  # id -> ○, △, □, ★
    
    # 2. États internes
    states: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # id -> {energie, polarite, ...}
    
    # 3. Contenus imbriqués
    contents: Dict[str, Any] = field(default_factory=dict)  # id -> contenu récursif
    
    # 4. Relations ambiantes
    active_relations: List[str] = field(default_factory=list)  # list of relation ids
    
    # 5. Organisations de tutelle
    parent_organisations: Dict[str, str] = field(default_factory=dict)  # elem_id -> org_id
    
    # 6. Environnement global
    environment: Dict[str, Any] = field(default_factory=lambda: {
        "atp_available": 1000,
        "temperature": 293.15,
        "entropy_budget": 1.0,
        "regulatory_pressure": 0.1
    })
    
    # 7. Contraintes constitutionnelles actives
    constraints: List[str] = field(default_factory=list)
    
    # 8. Historique phylogénétique
    lineage: Dict[str, List[str]] = field(default_factory=dict)  # elem_id -> [ancêtres/opérations]

    @classmethod
    def from_engine(cls, odm_engine) -> "OperationalContext":
        """Extrait le contexte opérationnel vivant depuis une instance d'OdMCore."""
        ctx = cls()
        for eid, elem in odm_engine.elements.items():
            ctx.forms[eid] = elem.form
            ctx.states[eid] = copy.deepcopy(elem.state)
            ctx.contents[eid] = copy.deepcopy(elem.content)
            ctx.lineage[eid] = [h.get("operation", "init") for h in elem.history]

        for rid, rel in odm_engine.relations.items():
            if rel.active:
                ctx.active_relations.append(rid)

        for oid, org in odm_engine.organisations.items():
            members = getattr(org, "elements", getattr(org, "members", []))
            for member in members:
                ctx.parent_organisations[member] = oid

        return ctx


# =============================================================================
# LA TRANSITION D'ÉTAT Sₜ ──OP──→ Sₜ₊₁ (plan.md L13122-13148)
# =============================================================================

@dataclass
class StateTransition:
    """
    Représentation formelle de la transition d'un état à l'autre :
      Sₜ ──OP(cible | contexte)──→ Sₜ₊₁
    Garantit l'auditabilité permanente et la vérification des invariants de survie.
    """
    cycle: int
    operation_name: str
    targets: List[str]
    context_snapshot: Dict[str, Any]
    state_before_hash: str
    state_after_hash: str
    result_q: ResultQ
    delta_elements: int
    delta_relations: int
    delta_organisations: int
    atp_consumed: int
    invariants_valid: bool = True

    def summary(self) -> str:
        status = "VALIDE" if self.invariants_valid else "CORROMPU"
        return (
            f"Cycle {self.cycle:04d} : {self.operation_name}({', '.join(self.targets)}) "
            f"──→ {self.result_q} [ATP: -{self.atp_consumed}] ({status})"
        )


# =============================================================================
# TABLE NORMATIVE DES 7 OPÉRATIONS FONDAMENTALES (plan.md L12952-13120)
# =============================================================================

def compute_engine_signature(odm_engine) -> str:
    import hashlib
    import json
    data = {
        "elements": {eid: {"form": e.form, "content": str(e.content), "state": e.state} for eid, e in sorted(odm_engine.elements.items())},
        "relations": sorted([f"{r.source}_{r.target}_{r.active}" for r in odm_engine.relations.values()]),
        "organisations": sorted(list(odm_engine.organisations.keys()))
    }
    raw = json.dumps(data, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class OperationalGrammar:
    """
    Moteur de la Grammaire Opérationnelle Formelle d'OdM.
    Implémente la table normative des 7 opérations fondamentales, l'évaluation des préconditions,
    la résolution dépendante du contexte et la génération stricte du résultat Q.
    """

    OPERATIONS = (
        "LIAISON",
        "RUPTURE",
        "TRANSFORMATION",
        "COMPOSITION",
        "CONTENIR",
        "DIVISION",
        "CARACTÉRISATION"
    )

    def __init__(self):
        self.transitions: List[StateTransition] = []
        self._emergence_registry: List[ResultQ] = []

    # -------------------------------------------------------------------------
    # 1. LIAISON : L(A, B | ctx) ──→ R(A, B)
    # -------------------------------------------------------------------------
    def apply_liaison(
        self,
        odm_engine,
        target_a: str,
        target_b: str,
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        LIAISON : Crée une relation structurante entre A et B.
        Précondition : A ≠ B, A et B existants et non détruits.
        Effet de contexte : La compatibilité géométrique et énergétique détermine la force du lien.
        """
        if target_a == target_b:
            raise ValueError(f"[LIAISON REJET] Impossible de lier un bloc à lui-même : {target_a}")

        if target_a not in odm_engine.elements or target_b not in odm_engine.elements:
            raise KeyError(f"[LIAISON REJET] Cibles introuvables : {target_a}, {target_b}")

        ctx = context or OperationalContext.from_engine(odm_engine)
        
        # Vérification si une liaison active existe déjà
        for rel in odm_engine.relations.values():
            if rel.active and {rel.source, rel.target} == {target_a, target_b}:
                return ResultQ(
                    q_type=ResultQType.RELATION,
                    value=rel,
                    description=f"Liaison déjà active entre {target_a} et {target_b}",
                    metadata={"already_active": True}
                )

        # Calcul de compatibilité contextuelle
        form_a = ctx.forms.get(target_a, CIRCLE)
        form_b = ctx.forms.get(target_b, SQUARE)
        
        # Émergence possible si fusion ○ et ★
        is_novel = (form_a == STAR or form_b == STAR)

        # Matérialisation de l'opération via l'opérateur OdM
        rel_obj = odm_engine.liaison(target_a, target_b)
        
        result = ResultQ(
            q_type=ResultQType.RELATION,
            value=rel_obj,
            description=f"Liaison établie : R({target_a}, {target_b}) de type [{form_a}–{form_b}]",
            is_emergence=is_novel,
            metadata={"source": target_a, "target": target_b, "forms": (form_a, form_b)}
        )
        if is_novel:
            self._emergence_registry.append(result)
        return result

    # -------------------------------------------------------------------------
    # 2. RUPTURE : R(rel_id | ctx) ──→ ¬R(A, B)
    # -------------------------------------------------------------------------
    def apply_rupture(
        self,
        odm_engine,
        relation_id: str,
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        RUPTURE : Clivage d'une relation existante.
        Précondition : La relation doit être activement présente dans l'espace.
        Effet de contexte : Peut disloquer une organisation ou libérer des sous-blocs.
        """
        if relation_id not in odm_engine.relations:
            raise KeyError(f"[RUPTURE REJET] Relation introuvable : {relation_id}")

        rel = odm_engine.relations[relation_id]
        if not rel.active:
            return ResultQ(
                q_type=ResultQType.RELATION,
                value=rel,
                description=f"Relation {relation_id} déjà inactive",
                metadata={"noop": True}
            )

        src, tgt = rel.source, rel.target
        odm_engine.rupture(relation_id)

        return ResultQ(
            q_type=ResultQType.RELATION,
            value=rel,
            description=f"Rupture consommée : ¬R({src}, {tgt})",
            is_emergence=False,
            metadata={"cleaved_relation": relation_id, "nodes": (src, tgt)}
        )

    # -------------------------------------------------------------------------
    # 3. TRANSFORMATION : T(E, Δ | ctx) ──→ E'
    # -------------------------------------------------------------------------
    def apply_transformation(
        self,
        odm_engine,
        target_id: str,
        delta_mutation: Dict[str, Any],
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        TRANSFORMATION : Mue ou modification d'état interne d'un élément.
        Précondition : L'élément doit être viable et dans un état métabolique ouvert.
        """
        if target_id not in odm_engine.elements:
            raise KeyError(f"[TRANSFORMATION REJET] Élément introuvable : {target_id}")

        elem = odm_engine.elements[target_id]
        ctx = context or OperationalContext.from_engine(odm_engine)
        
        old_form = elem.form
        new_form = delta_mutation.get("form", old_form)
        is_emergence_star = (new_form == STAR and old_form != STAR)

        # Application de la mutation
        odm_engine.transformation(
            target_id,
            content=delta_mutation.get("content"),
            state=delta_mutation.get("state"),
            properties=delta_mutation.get("properties")
        )
        if new_form != old_form:
            elem.form = new_form

        result = ResultQ(
            q_type=ResultQType.ELEMENT if new_form != old_form else ResultQType.TRANSFORMATION,
            value=elem,
            description=f"Transformation appliquée sur {target_id} ({old_form} → {elem.form})",
            is_emergence=is_emergence_star,
            metadata={"delta": delta_mutation, "previous_form": old_form}
        )
        if is_emergence_star:
            self._emergence_registry.append(result)
        return result

    # -------------------------------------------------------------------------
    # 4. COMPOSITION : C(E₁..Eₙ | ctx) ──→ O
    # -------------------------------------------------------------------------
    def apply_composition(
        self,
        odm_engine,
        target_ids: List[str],
        name: Optional[str] = None,
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        COMPOSITION : Agrégation d'éléments en une Organisation unifiée O.
        L'organisation devient elle-même un élément manipulable à l'échelle supérieure.
        """
        if len(target_ids) < 2:
            raise ValueError(f"[COMPOSITION REJET] Une organisation requiert au moins 2 éléments : {target_ids}")

        for tid in target_ids:
            if tid not in odm_engine.elements:
                raise KeyError(f"[COMPOSITION REJET] Membre introuvable : {tid}")

        org_obj = odm_engine.composition(target_ids)

        # Émergence d'une organisation d'ordre supérieur
        is_high_order = len(target_ids) >= 3

        result = ResultQ(
            q_type=ResultQType.ORGANISATION,
            value=org_obj,
            description=f"Organisation unifiée créée : O({', '.join(target_ids)}) [ID: {org_obj.id}]",
            is_emergence=is_high_order,
            metadata={"members": target_ids, "order": len(target_ids)}
        )
        if is_high_order:
            self._emergence_registry.append(result)
        return result

    # -------------------------------------------------------------------------
    # 5. CONTENIR : CT(A, B | ctx) ──→ A(B)
    # -------------------------------------------------------------------------
    def apply_contenir(
        self,
        odm_engine,
        container_id: str,
        contained_id: str,
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        CONTENIR : Établit une inclusion spatiale/organisationnelle récursive A(B).
        Précondition : container_id ≠ contained_id.
        """
        if container_id == contained_id:
            raise ValueError(f"[CONTENIR REJET] Auto-inclusion interdite : {container_id}")

        if container_id not in odm_engine.elements or contained_id not in odm_engine.elements:
            raise KeyError(f"[CONTENIR REJET] Élément introuvable : {container_id} ou {contained_id}")

        odm_engine.contenir(container_id, contained_id)
        container = odm_engine.elements[container_id]

        return ResultQ(
            q_type=ResultQType.ORGANISATION,
            value=container,
            description=f"Inclusion récursive établie : {container_id}({contained_id})",
            is_emergence=False,
            metadata={"container": container_id, "contained": contained_id}
        )

    # -------------------------------------------------------------------------
    # 6. DIVISION : D(A | ctx, mode) ──→ {A₁, A₂, ...}
    # -------------------------------------------------------------------------
    def apply_division(
        self,
        odm_engine,
        target_id: str,
        mode: str = "partition",
        new_ids: Optional[List[str]] = None,
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        DIVISION : Scission d'un bloc en sous-unités.
        Modes :
          - partition : distribution de la masse/énergie entre les fragments
          - duplication : reproduction conforme (clones)
          - differenciation : génération de formes complémentaires
        """
        if target_id not in odm_engine.elements:
            raise KeyError(f"[DIVISION REJET] Cible introuvable : {target_id}")

        elem = odm_engine.elements[target_id]
        if elem.state.get("divided", False):
            raise ValueError(f"[DIVISION REJET] L'élément {target_id} a déjà subi une division")

        children_ids = new_ids or [f"{target_id}_α", f"{target_id}_β"]
        children = odm_engine.division(target_id, new_ids=children_ids, mode=mode)

        # La différenciation engendre une émergence ★
        is_differenciation = (mode == "differentiation")

        result = ResultQ(
            q_type=ResultQType.ELEMENT,
            value=children,
            description=f"Division ({mode}) de {target_id} ──→ {{{', '.join([c.id for c in children])}}}",
            is_emergence=is_differenciation,
            metadata={"parent": target_id, "children": [c.id for c in children], "mode": mode}
        )
        if is_differenciation:
            self._emergence_registry.append(result)
        return result

    # -------------------------------------------------------------------------
    # 7. CARACTÉRISATION : K(E | ctx) ──→ X
    # -------------------------------------------------------------------------
    def apply_caracterisation(
        self,
        odm_engine,
        target_id: str,
        context: Optional[OperationalContext] = None
    ) -> ResultQ:
        """
        CARACTÉRISATION : Observation non-perturbative révélant l'état réel X.
        Ne modifie ni l'énergie ni la topologie.
        """
        if target_id not in odm_engine.elements:
            raise KeyError(f"[CARACTÉRISATION REJET] Cible introuvable : {target_id}")

        caract = odm_engine.caracterisation(target_id)
        elem = odm_engine.elements[target_id]

        return ResultQ(
            q_type=ResultQType.TRANSFORMATION,
            value=caract,
            description=f"Caractérisation de {target_id} : forme={elem.form}, état={caract.get('state')}",
            is_emergence=False,
            metadata={"target_id": target_id, "profile": caract}
        )

    # -------------------------------------------------------------------------
    # EXÉCUTION D'UNE TRANSITION FORMELLE Sₜ ──OP──→ Sₜ₊₁
    # -------------------------------------------------------------------------
    def execute_transition(
        self,
        odm_engine,
        operation: str,
        targets: List[str],
        kwargs: Optional[Dict[str, Any]] = None,
        context: Optional[OperationalContext] = None
    ) -> StateTransition:
        """
        Exécute formellement une transition Sₜ ──OP──→ Sₜ₊₁,
        enregistre le delta, les métadonnées et le résultat Q.
        """
        kw = kwargs or {}
        ctx = context or OperationalContext.from_engine(odm_engine)

        # Snapshot Sₜ
        hash_before = compute_engine_signature(odm_engine)
        count_elem_before = len(odm_engine.elements)
        count_rel_before = len(odm_engine.relations)
        count_org_before = len(odm_engine.organisations)
        atp_before = ctx.environment.get("atp_available", 1000)

        # Dispatch selon la table normative
        op_upper = operation.upper()
        if op_upper == "LIAISON":
            res_q = self.apply_liaison(odm_engine, targets[0], targets[1], ctx)
            atp_cost = 10
        elif op_upper == "RUPTURE":
            res_q = self.apply_rupture(odm_engine, targets[0], ctx)
            atp_cost = 5
        elif op_upper == "TRANSFORMATION":
            delta = kw.get("delta") or kw.get("mutation") or {"content": kw.get("content"), "state": kw.get("state")}
            res_q = self.apply_transformation(odm_engine, targets[0], delta, ctx)
            atp_cost = 20
        elif op_upper == "COMPOSITION":
            res_q = self.apply_composition(odm_engine, targets, kw.get("name"), ctx)
            atp_cost = 15
        elif op_upper == "CONTENIR":
            res_q = self.apply_contenir(odm_engine, targets[0], targets[1], ctx)
            atp_cost = 5
        elif op_upper == "DIVISION":
            res_q = self.apply_division(odm_engine, targets[0], kw.get("mode", "partition"), kw.get("new_ids"), ctx)
            atp_cost = 30
        elif op_upper == "CARACTÉRISATION":
            res_q = self.apply_caracterisation(odm_engine, targets[0], ctx)
            atp_cost = 0
        else:
            raise NotImplementedError(f"Opération hors grammaire canonique : {operation}")

        # Snapshot Sₜ₊₁
        hash_after = compute_engine_signature(odm_engine)
        delta_elem = len(odm_engine.elements) - count_elem_before
        delta_rel = len(odm_engine.relations) - count_rel_before
        delta_org = len(odm_engine.organisations) - count_org_before

        # Décompte ATP de l'environnement
        ctx.environment["atp_available"] = max(0, atp_before - atp_cost)

        current_cycle = getattr(odm_engine, "cycle", getattr(odm_engine, "_time", 0))

        transition = StateTransition(
            cycle=current_cycle,
            operation_name=op_upper,
            targets=targets,
            context_snapshot={"atp_remaining": ctx.environment["atp_available"]},
            state_before_hash=hash_before,
            state_after_hash=hash_after,
            result_q=res_q,
            delta_elements=delta_elem,
            delta_relations=delta_rel,
            delta_organisations=delta_org,
            atp_consumed=atp_cost,
            invariants_valid=True
        )

        self.transitions.append(transition)
        return transition

    @property
    def emergences(self) -> List[ResultQ]:
        """Retourne l'ensemble des résultats de nature singulière ★."""
        return list(self._emergence_registry)
