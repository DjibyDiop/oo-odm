from typing import List, Dict, Any
from meo_engine import State

class ConstitutionRules:
    """
    Système de règles de l'Organisme d'OO (Zéro Mocks).
    Base ses contraintes sur la Thermodynamique et le WardenTribunal (oo-constitution).
    """
    
    @staticmethod
    def filter_possibilities(state: State, possibilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtre les possibilités brutes en appliquant les lois de la constitution.
        """
        valid_possibilities = []
        
        atp_pool = state.global_properties.get("atp_pool", 0)
        quarantine_zone = state.global_properties.get("quarantine_zone", [])
        
        for p in possibilities:
            # 1. Règle Thermodynamique (EnergyConservation / ATPRegulator)
            cost = p.get("atp_cost", 0)
            if cost > atp_pool:
                continue # Rejeté par manque d'énergie
                
            # 2. Règle Judiciaire (WardenTribunal)
            args = p.get("args", {})
            involved_elements = [v for k, v in args.items() if "id" in k]
            
            is_quarantined = any(elem_id in quarantine_zone for elem_id in involved_elements)
            if is_quarantined:
                # La Constitution interdit d'interagir avec des cellules en quarantaine
                continue
                
            # Si passe tous les filtres constitutionnels, c'est une opération déclenchable
            valid_possibilities.append(p)
            
        return valid_possibilities
