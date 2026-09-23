"""
OO-ODM — Organique des Matières
odm_core_v02/odm/metrics.py : Système de Mesure Organique

Spécification formelle selon plan.md (lignes 1106 → 1178, 9721 → 9750) :
  1. Profondeur organique (profondeur phylogénétique et hiérarchique) :
     - Niveau 0 : Blocs primordiaux
     - Niveau 1 : Premières compositions / liaisons
     - Niveau 2 : Interactions et transformations d'état
     - Niveau 3 : Émergences ★
     - Niveau 4+ : Émergences d'émergences
  2. Distance organique entre configurations de matière (morphologique + topologique + informationnelle)
  3. Richesse d'émergence (taux de singularité, variété d'émergences, indice de surprise non-linéaire)

RÈGLE ABSOLUE : ZÉRO MOCKS.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .element import Element, CIRCLE, TRIANGLE, SQUARE, STAR
from .relation import Relation
from .organisation import Organisation


@dataclass
class OrganicMeasurement:
    """
    Rapport d'audit métrologique d'un état ou d'une trajectoire OdM.
    """
    cycle: int
    profondeur_max: int
    profondeur_moyenne: float
    complexite_topologique: float
    entropie_shannon: float
    richesse_emergence: float
    stabilite_globale: float
    details: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"[Mesure Organique @ t={self.cycle}] "
            f"Profondeur: {self.profondeur_max} | "
            f"Entropie H: {self.entropie_shannon:.3f} bits | "
            f"Richesse ★: {self.richesse_emergence:.2%} | "
            f"Stabilité: {self.stabilite_globale:.2f}"
        )


class OrganicMetrics:
    """
    Moteur de métrologie organique d'OdM.
    """

    @classmethod
    def compute_element_depth(cls, element: Element) -> int:
        """
        Calcule la profondeur phylogénétique d'un bloc individuel (plan.md L1106-1130).
        - 0 : Primordial (aucune opération subie)
        - 1 : Simple liaison ou division
        - 2 : Multi-transformé
        - 3+ : Issu d'émergence ou de scission avancée
        """
        history = element.history or []
        relations = element.relations or []
        depth = len(history) + len(relations)

        # Majoration si forme Étoile ★ (émergence intrinsèque)
        if element.form == STAR:
            depth = max(depth, 3)

        # Majoration si imbriqué ou divisé
        if element.state.get("divided", False):
            depth += 1

        contains = element.state.get("contains", [])
        if contains:
            depth += len(contains)

        return depth

    @classmethod
    def compute_engine_depth(cls, odm_engine) -> Tuple[int, float]:
        """
        Calcule la profondeur maximale et la profondeur moyenne sur l'ensemble de l'écosystème.
        """
        if not odm_engine.elements:
            return 0, 0.0

        depths = [cls.compute_element_depth(e) for e in odm_engine.elements.values()]
        max_d = max(depths)
        avg_d = sum(depths) / len(depths)
        return max_d, round(avg_d, 2)

    @classmethod
    def compute_organic_distance(
        cls,
        state_a: Dict[str, Any],
        state_b: Dict[str, Any]
    ) -> float:
        """
        Calcule la distance organique D(S_A, S_B) ∈ [0, ∞[ entre deux états de matière.
        Combine :
          1. Distance morphologique (formes des blocs)
          2. Distance relationnelle (graphe de Hamming)
          3. Distance hiérarchique (organisations)
        """
        elems_a = state_a.get("elements", {})
        elems_b = state_b.get("elements", {})

        all_ids = set(elems_a.keys()).union(set(elems_b.keys()))
        if not all_ids:
            return 0.0

        # 1. Écart d'inventaire et de formes
        morpho_dist = 0.0
        for eid in all_ids:
            if eid not in elems_a or eid not in elems_b:
                morpho_dist += 1.0  # Apparition ou disparition
            else:
                form_a = elems_a[eid].get("form")
                form_b = elems_b[eid].get("form")
                if form_a != form_b:
                    morpho_dist += 0.5  # Mutation de forme

        # 2. Écart de relations
        rels_a = set(state_a.get("relations", []))
        rels_b = set(state_b.get("relations", []))
        rel_diff = len(rels_a.symmetric_difference(rels_b))

        # 3. Écart d'organisations
        orgs_a = len(state_a.get("organisations", []))
        orgs_b = len(state_b.get("organisations", []))
        org_diff = abs(orgs_a - orgs_b)

        # Distance combinée normalisée
        total_dist = morpho_dist + (0.8 * rel_diff) + (1.2 * org_diff)
        return round(total_dist, 3)

    @classmethod
    def compute_emergence_richness(
        cls,
        emergences: List[Any],
        total_transitions: int
    ) -> float:
        """
        Richesse d'émergence R_★ = N_★ / max(1, N_trans).
        Mesure le rendement en singularités novatrices du système.
        """
        if total_transitions == 0:
            return 0.0
        return round(len(emergences) / total_transitions, 4)

    @classmethod
    def compute_shannon_entropy(cls, odm_engine) -> float:
        """
        Entropie informationnelle de Shannon de la distribution des formes dans l'espace.
        H = - Σ p_i * log2(p_i)
        """
        elements = list(odm_engine.elements.values())
        if not elements:
            return 0.0

        counts: Dict[str, int] = {}
        for e in elements:
            counts[e.form] = counts.get(e.form, 0) + 1

        total = len(elements)
        entropy = 0.0
        for cnt in counts.values():
            p = cnt / total
            if p > 0:
                entropy -= p * math.log2(p)

        return round(entropy, 3)

    @classmethod
    def measure_full(cls, odm_engine, grammar_engine=None) -> OrganicMeasurement:
        """
        Effectue une mesure complète de l'état organique instantané.
        """
        max_d, avg_d = cls.compute_engine_depth(odm_engine)
        entropy = cls.compute_shannon_entropy(odm_engine)

        emergence_count = len(grammar_engine.emergences) if grammar_engine else 0
        trans_count = len(grammar_engine.transitions) if grammar_engine else max(1, odm_engine.cycle)
        richness = cls.compute_emergence_richness(
            grammar_engine.emergences if grammar_engine else [],
            trans_count
        )

        # Complexité topologique : ratio arêtes / sommets
        v_count = max(1, len(odm_engine.elements))
        e_count = len([r for r in odm_engine.relations.values() if r.active])
        topological_complexity = round(e_count / v_count, 3)

        # Stabilité globale
        stability = 0.85
        if odm_engine.elements:
            stars = sum(1 for e in odm_engine.elements.values() if e.form == STAR)
            if stars > v_count / 2:
                stability = 0.65  # Forte instabilité créatrice

        return OrganicMeasurement(
            cycle=odm_engine.cycle,
            profondeur_max=max_d,
            profondeur_moyenne=avg_d,
            complexite_topologique=topological_complexity,
            entropie_shannon=entropy,
            richesse_emergence=richness,
            stabilite_globale=stability,
            details={
                "elements_count": v_count,
                "active_relations": e_count,
                "organisations_count": len(odm_engine.organisations),
                "emergence_count": emergence_count
            }
        )
