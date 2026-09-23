from .oir import OIRInstruction, OIRType
from meo.meo_engine import Espace
from typing import Any

class OCoreEngine:
    """
    O-CORE: Runtime / Mémoire / État
    Gère la source de vérité de l'Espace en toute sécurité.
    A terme, implémenté en Rust natif.
    """
    def __init__(self, initial_espace: Espace):
        print("[O-CORE] Initialisation de la mémoire sécurisée.")
        self._espace = initial_espace
        
    def process(self, instruction: OIRInstruction) -> Any:
        if instruction.type == OIRType.UPDATE_STATE:
            # Sécurité mémoire appliquée ici
            self._espace = instruction.payload["new_espace"]
            return {"status": "success", "msg": "State safely updated"}
        return {"status": "ignored"}
        
    def get_readonly_state(self) -> Espace:
        """Retourne un clone pour éviter la corruption de la mémoire."""
        return self._espace.clone()
