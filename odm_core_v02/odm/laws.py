"""
OO-ODM — Organique des Matières
odm_core_v02/odm/laws.py : Système de Lois, Conditions et Stabilité

Spécification formelle selon plan.md (lignes 9570 → 9810) :
  1. Typologie des conditions : nécessaire, suffisante, bloquante, facilitatrice, émergente
  2. Évolution des capacités et trajectoires
  3. Modélisation de la stabilité : stable, métastable, instable, chaotique
  4. Lois fondamentales de la matière :
     - Loi I   : Conservation et Bilan Énergétique (Métabolisme)
     - Loi II  : Affinité et Compatibilité Morphologique (○, △, □, ★)
     - Loi III : Mutation du Champ des Possibles (Π(E') ≠ Π(E))
     - Loi IV  : Dégradation et Homéostasie Organique

RÈGLE ABSOLUE : ZÉRO MOCKS.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .element import Element, CIRCLE, TRIANGLE, SQUARE, STAR
from .relation import Relation
from .organisation import Organisation


# =============================================================================
# TYPOLOGIE DES CONDITIONS (plan.md L9590-9600)
# =============================================================================

class ConditionType(Enum):
    NECESSAIRE    = "NECESSAIRE"     # Sans elle, l'opération est physiquement impossible
    SUFFISANTE    = "SUFFISANTE"     # Sa seule présence déclenche l'opération
    BLOQUANTE     = "BLOQUANTE"      # Sa présence interdit formellement l'opération (Warden)
    FACILITATRICE = "FACILITATRICE"  # Réduit le coût énergétique ou le seuil de déclenchement
    EMERGENTE     = "EMERGENTE"      # Condition apparue spontanément suite à une réorganisation


@dataclass
class Condition:
    name: str
    condition_type: ConditionType
    predicate: Callable[[Any, Dict[str, Any]], bool]
    description: str = ""

    def evaluate(self, target: Any, context: Dict[str, Any]) -> bool:
        try:
            return self.predicate(target, context)
        except Exception:
            return False


# =============================================================================
# RÉGIMES DE STABILITÉ (plan.md L9688-9720)
# =============================================================================

class StabilityRegime(Enum):
    STABLE     = "STABLE"      # L'organisation absorbe les perturbations sans rompre
    METASTABLE = "METASTABLE"  # Stable localement, bifurque si perturbation critique
    INSTABLE   = "INSTABLE"    # Dislocation ou décomposition imminente
    CHAOTIQUE  = "CHAOTIQUE"   # Fluctuations imprévisibles, divergence des trajectoires


@dataclass
class StabilityMetrics:
    coherence_index: float  # [0.0, 1.0] : Cohésion interne
    energy_stress: float    # [0.0, 1.0] : Tension thermodynamique
    regime: StabilityRegime
    diagnostic: str


class StabilityEvaluator:
    """
    Évalue la stabilité intrinsèque des blocs et organisations de matière.
    """

    @staticmethod
    def evaluate_element(element: Element) -> StabilityMetrics:
        """Évalue la stabilité d'un élément unique."""
        energy = 100.0
        if isinstance(element.content, dict):
            energy = float(element.content.get("energie", 100))
        elif isinstance(element.content, (int, float)):
            energy = float(element.content)

        # Les étoiles ★ sont métastables par nature (forte dynamique)
        if element.form == STAR:
            regime = StabilityRegime.METASTABLE
            coherence = 0.75
            stress = 0.6
            diag = "Singularité émergente active (métastable)"
        elif element.form == SQUARE:
            regime = StabilityRegime.STABLE
            coherence = 0.95
            stress = 0.1
            diag = "Structure stabilisatrice cubique (haute inertie)"
        elif element.form == TRIANGLE:
            regime = StabilityRegime.METASTABLE
            coherence = 0.8
            stress = 0.35
            diag = "Vecteur directionnel orienté (stabilité dynamique)"
        else: # CIRCLE
            regime = StabilityRegime.STABLE
            coherence = 0.9
            stress = 0.15
            diag = "Potentiel fermé réceptif"

        # Modulation par l'énergie
        if energy > 500:
            regime = StabilityRegime.INSTABLE
            stress = min(1.0, stress * 2.0)
            diag += " [Surcharge d'énergie interne]"

        return StabilityMetrics(
            coherence_index=coherence,
            energy_stress=stress,
            regime=regime,
            diagnostic=diag
        )

    @staticmethod
    def evaluate_organisation(org: Organisation, odm_engine) -> StabilityMetrics:
        """Évalue la stabilité systémique d'une organisation complète."""
        members = getattr(org, "elements", getattr(org, "members", []))
        member_count = len(members)
        if member_count == 0:
            return StabilityMetrics(0.0, 1.0, StabilityRegime.INSTABLE, "Organisation vide")

        # Liens internes actifs
        active_internal_links = 0
        member_set = set(members)
        for rel in odm_engine.relations.values():
            if rel.active and rel.source in member_set and rel.target in member_set:
                active_internal_links += 1

        # Densité de connectivité : liens / liens_max
        max_possible_links = (member_count * (member_count - 1)) / 2 if member_count > 1 else 1
        density = active_internal_links / max_possible_links

        if density >= 0.6:
            regime = StabilityRegime.STABLE
            coherence = min(1.0, 0.7 + density * 0.3)
            stress = 0.2
            diag = f"Organisation maillée résiliente ({active_internal_links} liens internes)"
        elif density >= 0.2:
            regime = StabilityRegime.METASTABLE
            coherence = 0.5 + density * 0.4
            stress = 0.45
            diag = f"Organisation lâche métastable ({active_internal_links} liens internes)"
        else:
            regime = StabilityRegime.INSTABLE
            coherence = 0.25
            stress = 0.85
            diag = "Déficit structurel critique : risque de dislocation"

        return StabilityMetrics(
            coherence_index=round(coherence, 3),
            energy_stress=round(stress, 3),
            regime=regime,
            diagnostic=diag
        )


# =============================================================================
# LES LOIS FONDAMENTALES DE L'ORGANIQUE DES MATIÈRES (plan.md L9751-9782)
# =============================================================================

class LawVerdict:
    def __init__(self, allowed: bool, law_name: str, explanation: str, atp_penalty: int = 0):
        self.allowed = allowed
        self.law_name = law_name
        self.explanation = explanation
        self.atp_penalty = atp_penalty

    def __repr__(self) -> str:
        res = "CONFORME" if self.allowed else "VIOLATION"
        return f"[{self.law_name}] {res} : {self.explanation}"


class LawsOfMatter:
    """
    Système axiomatique des lois régissant la matière dans OdM.
    """

    # Matrice d'affinité morphologique (○, △, □, ★)
    # Lignes: Forme Source, Colonnes: Forme Cible -> Score d'affinité [0.0 - 1.0]
    AFFINITY_MATRIX: Dict[Tuple[str, str], float] = {
        (CIRCLE, CIRCLE):     0.80, # Fusion de réservoirs
        (CIRCLE, TRIANGLE):   0.95, # Réservoir + Vecteur = Flux accéléré (haute synergie)
        (CIRCLE, SQUARE):     0.70, # Conteneur + Stabilisateur
        (CIRCLE, STAR):       0.90, # Émergence captée par un récipient
        (TRIANGLE, TRIANGLE): 0.60, # Collision vectorielle (forte tension)
        (TRIANGLE, SQUARE):   0.85, # Vecteur ancré dans une base stable
        (TRIANGLE, STAR):     0.95, # Propulsion de singularité
        (SQUARE, SQUARE):     0.90, # Agrégation cristalline solide
        (SQUARE, STAR):       0.50, # Confinement difficile d'une singularité
        (STAR, STAR):         0.40, # Répulsion de singularités multiples
    }

    @classmethod
    def get_morphological_affinity(cls, form_a: str, form_b: str) -> float:
        """Retourne le coefficient de résonance morphologique symétrique entre deux formes."""
        key = (form_a, form_b)
        rev_key = (form_b, form_a)
        return cls.AFFINITY_MATRIX.get(key, cls.AFFINITY_MATRIX.get(rev_key, 0.50))

    @staticmethod
    def check_law_conservation(operation: str, atp_cost: int, available_atp: int) -> LawVerdict:
        """
        Loi I : Conservation et Bilan Énergétique
        Aucune transformation ne peut se produire sans allocation d'énergie métabolique.
        """
        if atp_cost > available_atp:
            return LawVerdict(
                allowed=False,
                law_name="LOI_I_CONSERVATION_ENERGIE",
                explanation=f"Rejet : Coût requis ({atp_cost} ATP) supérieur à la réserve ({available_atp} ATP)"
            )
        return LawVerdict(
            allowed=True,
            law_name="LOI_I_CONSERVATION_ENERGIE",
            explanation=f"Approuvé : Solde résiduel = {available_atp - atp_cost} ATP"
        )

    @classmethod
    def check_law_morphology(cls, form_a: str, form_b: str) -> LawVerdict:
        """
        Loi II : Affinité Morphologique
        Certaines topologies de liaison requièrent un seuil d'affinité minimal pour perdurer.
        """
        affinity = cls.get_morphological_affinity(form_a, form_b)
        if affinity < 0.45:
            return LawVerdict(
                allowed=False,
                law_name="LOI_II_AFFINITE_MORPHOLOGIQUE",
                explanation=f"Répulsion géométrique : Affinité [{form_a}–{form_b}] = {affinity:.2f} (< 0.45)",
                atp_penalty=25
            )
        return LawVerdict(
            allowed=True,
            law_name="LOI_II_AFFINITE_MORPHOLOGIQUE",
            explanation=f"Affinité valide [{form_a}–{form_b}] = {affinity:.2f}"
        )

    @staticmethod
    def check_law_possibility_mutation(element_before: Element, element_after: Element) -> LawVerdict:
        """
        Loi III : Mutation du Champ des Possibles
        La modification du contenu ou de l'état altère obligatoirement le spectre des trajectoires futures.
        """
        changed = (
            element_before.form != element_after.form or
            element_before.content != element_after.content or
            element_before.state != element_after.state
        )
        if changed:
            return LawVerdict(
                allowed=True,
                law_name="LOI_III_MUTATION_POSSIBILITES",
                explanation="Nouvelles branches du champ déverrouillées suite à mutation"
            )
        return LawVerdict(
            allowed=True,
            law_name="LOI_III_MUTATION_POSSIBILITES",
            explanation="Trajectoire stationnaire (pas de bifurcation)"
        )
