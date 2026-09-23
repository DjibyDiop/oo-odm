"""
OdM — Organique des Matières
Organisation : regroupement structuré d'éléments.

Une Organisation :
  - possède un identifiant unique (O1, O2, …)
  - référence plusieurs éléments par leur id
  - référence les relations internes
  - conserve son propre historique d'évolution

Notations OdM :
    C(A, B, C) → O1    (COMPOSITION produit une Organisation)
    CT(A, B)           (CONTENIR inscrit B dans l'état de A)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


# ============================================================
# ORGANISATION
# ============================================================

@dataclass
class Organisation:
    id:        str
    elements:  List[str]           = field(default_factory=list)
    relations: List[str]           = field(default_factory=list)
    history:   List[Dict[str, Any]] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"{self.id}: éléments={self.elements}"
