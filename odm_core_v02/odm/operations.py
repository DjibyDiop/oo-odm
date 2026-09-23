"""
OdM — Organique des Matières
Règles des 7 opérations fondamentales.

Chaque règle vérifie les préconditions d'une opération
avant qu'elle soit exécutée par le moteur.

R1 : LIAISON     — nécessite deux éléments existants et distincts
R2 : RUPTURE     — nécessite une relation active existante
R3 : TRANSFORMATION — modifie au moins une caractéristique de l'élément
R4 : COMPOSITION — nécessite ≥ 2 éléments distincts
R5 : CONTENIR    — nécessite un contenant et un contenu distincts existants
R6 : DIVISION    — produit ≥ 2 éléments avec des identifiants nouveaux
R7 : CARACTÉRISATION — ne transforme pas la cible (lecture seule)
"""

from typing import Any, Dict, List, Optional


class RuleViolation(Exception):
    """Levée lorsqu'une précondition d'opération n'est pas satisfaite."""
    pass


class Operations:
    """
    Catalogue des règles de validation des 7 opérations OdM.
    Utilisé par OdMCore avant chaque opération.
    """

    # --------------------------------------------------------
    # R1 — LIAISON
    # --------------------------------------------------------

    @staticmethod
    def check_liaison(
        elements: Dict[str, Any],
        a_id: str,
        b_id: str
    ) -> None:
        if a_id not in elements:
            raise RuleViolation(
                f"R1 — LIAISON : l'élément '{a_id}' n'existe pas."
            )
        if b_id not in elements:
            raise RuleViolation(
                f"R1 — LIAISON : l'élément '{b_id}' n'existe pas."
            )
        if a_id == b_id:
            raise RuleViolation(
                f"R1 — LIAISON : un élément ne peut pas se lier à lui-même."
            )

    # --------------------------------------------------------
    # R2 — RUPTURE
    # --------------------------------------------------------

    @staticmethod
    def check_rupture(
        relations: Dict[str, Any],
        relation_id: str
    ) -> None:
        if relation_id not in relations:
            raise RuleViolation(
                f"R2 — RUPTURE : la relation '{relation_id}' n'existe pas."
            )
        if not relations[relation_id].active:
            raise RuleViolation(
                f"R2 — RUPTURE : la relation '{relation_id}' est déjà rompue."
            )

    # --------------------------------------------------------
    # R3 — TRANSFORMATION
    # --------------------------------------------------------

    @staticmethod
    def check_transformation(
        elements: Dict[str, Any],
        element_id: str,
        content: Any,
        state: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        capacities: Optional[Dict] = None,
    ) -> None:
        if element_id not in elements:
            raise RuleViolation(
                f"R3 — TRANSFORMATION : l'élément '{element_id}' n'existe pas."
            )
        if all(x is None for x in [content, state, properties, capacities]):
            raise RuleViolation(
                "R3 — TRANSFORMATION : au moins une caractéristique "
                "doit être modifiée (contenu, état, propriétés ou capacités)."
            )

    # --------------------------------------------------------
    # R4 — COMPOSITION
    # --------------------------------------------------------

    @staticmethod
    def check_composition(
        elements: Dict[str, Any],
        element_ids: List[str]
    ) -> None:
        if len(element_ids) < 2:
            raise RuleViolation(
                "R4 — COMPOSITION : nécessite au moins 2 éléments."
            )
        for eid in element_ids:
            if eid not in elements:
                raise RuleViolation(
                    f"R4 — COMPOSITION : l'élément '{eid}' n'existe pas."
                )
        if len(set(element_ids)) != len(element_ids):
            raise RuleViolation(
                "R4 — COMPOSITION : les éléments doivent être distincts."
            )

    # --------------------------------------------------------
    # R5 — CONTENIR
    # --------------------------------------------------------

    @staticmethod
    def check_contenir(
        elements: Dict[str, Any],
        container_id: str,
        element_id: str
    ) -> None:
        if container_id not in elements:
            raise RuleViolation(
                f"R5 — CONTENIR : le contenant '{container_id}' n'existe pas."
            )
        if element_id not in elements:
            raise RuleViolation(
                f"R5 — CONTENIR : le contenu '{element_id}' n'existe pas."
            )
        if container_id == element_id:
            raise RuleViolation(
                "R5 — CONTENIR : un élément ne peut pas se contenir lui-même."
            )

    # --------------------------------------------------------
    # R6 — DIVISION
    # --------------------------------------------------------

    @staticmethod
    def check_division(
        elements: Dict[str, Any],
        element_id: str,
        new_ids: List[str]
    ) -> None:
        if element_id not in elements:
            raise RuleViolation(
                f"R6 — DIVISION : l'élément '{element_id}' n'existe pas."
            )
        if len(new_ids) < 2:
            raise RuleViolation(
                "R6 — DIVISION : une division nécessite au moins 2 nouveaux éléments."
            )
        for new_id in new_ids:
            if new_id in elements:
                raise RuleViolation(
                    f"R6 — DIVISION : l'identifiant '{new_id}' existe déjà."
                )

    # --------------------------------------------------------
    # R7 — CARACTÉRISATION
    # --------------------------------------------------------

    @staticmethod
    def check_caracterisation(
        elements: Dict[str, Any],
        element_id: str
    ) -> None:
        if element_id not in elements:
            raise RuleViolation(
                f"R7 — CARACTÉRISATION : l'élément '{element_id}' n'existe pas."
            )
