"""
OdM — Organique des Matières
Relation : lien entre deux éléments.

Une Relation :
  - possède un identifiant unique (R1, R2, …)
  - désigne une source et une cible
  - peut être active ou rompue (RUPTURE)

Notations OdM :
    L(A, B)  → crée une relation active entre A et B
    R(Rn)    → rompt la relation Rn
"""

from dataclasses import dataclass


# ============================================================
# RELATION
# ============================================================

@dataclass
class Relation:
    id:     str
    source: str
    target: str
    active: bool = True

    def __repr__(self) -> str:
        status = "active" if self.active else "rompue"
        return f"{self.id}: {self.source} → {self.target} [{status}]"
