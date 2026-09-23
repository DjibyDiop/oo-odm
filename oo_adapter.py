import json
try:
    from meo.constraints import ConstraintProvider, ConstraintCategory
    from meo.meo_engine import Espace
except (ImportError, ValueError):
    from .meo.constraints import ConstraintProvider, ConstraintCategory
    from .meo.meo_engine import Espace
from typing import Dict, Any

class OOConstitutionalProvider(ConstraintProvider):
    """
    Adaptateur qui connecte le MEO au monde spécifique de l'organisme OO.
    Il lit les propriétés de l'état (alimenté par la constitution.plus) et impose
    les limites d'ATP (Thermodynamique) et de Quarantaine (Judiciaire).
    """
    def name(self) -> str:
        return "OO_Constitution_Adapter"
        
    def __init__(self, constitution_path: str = "constitution.plus"):
        self.constitution_path = constitution_path
        self._load_constitution()
        
    def _load_constitution(self):
        # Lecture / parsing de la constitution OO
        self.rules = {
            "max_atp_per_cycle": 200,
            "forbidden_elements": ["WardenTribunal"], # Un élément en quarantaine
            "min_atp_reserve": 100
        }

    def evaluate(self, espace: Espace, transformation_data: Dict[str, Any]) -> tuple[bool, str]:
        # Règle 1: Ressources (ATP)
        cost = transformation_data.get("atp_cost", 0)
        if cost > self.rules["max_atp_per_cycle"]:
            return False, f"Violation Constitution: Coût ATP ({cost}) dépasse le maximum autorisé ({self.rules['max_atp_per_cycle']})"
            
        current_atp = espace.global_properties.get("atp_pool", 0)
        if current_atp - cost < self.rules["min_atp_reserve"]:
            return False, f"Violation Constitution: Réserve ATP critique (Restant: {current_atp - cost} < Min: {self.rules['min_atp_reserve']})"

        # Règle 2: Sécurité (Quarantaine)
        quarantine = espace.global_properties.get("quarantine_zone", [])
        args = transformation_data.get("args", {})
        for arg_key, bloc_id in args.items():
            if "id" in arg_key:
                if bloc_id in quarantine:
                    return False, f"Violation Constitution: Élément {bloc_id} est sous restriction de quarantaine"
                if bloc_id in espace.blocs:
                    bloc = espace.blocs[bloc_id]
                    if bloc.name in self.rules["forbidden_elements"] or bloc.id in quarantine:
                        return False, f"Violation Constitution: Bloc {bloc.name} est sous restriction de sécurité"

        return True, "VALID"
