from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .meo_engine import Espace

class ConstraintCategory(Enum):
    PHYSICAL = auto()
    CONSTITUTIONAL = auto()
    RESOURCE = auto()
    SAFETY = auto()

class ConstraintProvider(ABC):
    """
    Interface abstraite pour filtrer les possibilités d'OdM.
    Garantit l'indépendance du MEO : le moteur ne connaît pas le monde dans lequel il évolue.
    """
    
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def evaluate(self, espace: Espace, possibility: Dict[str, Any]) -> tuple[bool, str]:
        """
        Évalue si une possibilité est valide.
        Retourne (is_valid, reason_if_invalid).
        """
        pass
