"""
OdM — Organique des Matières
Unité fondamentale : l'Élément.

Un Élément possède :
  - une forme    (symbole de l'alphabet organique)
  - un contenu   (valeur ou structure arbitraire)
  - un état      (dictionnaire de clés/valeurs dynamiques)
  - des propriétés (caractéristiques stables)
  - des capacités  (ce que l'élément peut faire)
  - une liste de relations actives
  - un historique de toutes ses transformations

Notations OdM :
    ○A, △B, □C  — éléments de formes différentes
    A₀ → A₁     — historique d'états
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import copy


# ============================================================
# ALPHABET DES FORMES
# ============================================================

CIRCLE   = "○"   # forme fondamentale 1
TRIANGLE = "△"   # forme fondamentale 2
SQUARE   = "□"   # forme fondamentale 3
STAR     = "★"   # forme d'émergence


# ============================================================
# ÉLÉMENT
# ============================================================

@dataclass
class Element:
    """
    Unité condensée de connaissance ou de possibilité.

    B = {structure, relations, propriétés, possibilités, contraintes}
    """

    id:         str
    form:       str
    content:    Any

    state:      Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    capacities: Dict[str, Any] = field(default_factory=dict)
    relations:  List[str]      = field(default_factory=list)
    history:    List[Dict[str, Any]] = field(default_factory=list)

    # --------------------------------------------------------
    # Instantané — avant/après toute opération
    # --------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Retourne une copie complète de l'état courant."""
        return {
            "id":         self.id,
            "form":       self.form,
            "content":    copy.deepcopy(self.content),
            "state":      copy.deepcopy(self.state),
            "properties": copy.deepcopy(self.properties),
            "capacities": copy.deepcopy(self.capacities),
            "relations":  list(self.relations),
        }

    def __repr__(self) -> str:
        return (
            f"{self.form}{self.id}"
            f" | contenu={self.content}"
            f" | état={self.state}"
            f" | relations={self.relations}"
        )
