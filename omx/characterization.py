from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.meo_engine import Espace
from meo.experiment import TrajectoryNode
from meo.comparer import Comparer

class CharacterizationEngine:
    """
    O-CHARACTERIZATION: Moteur d'Émergence / Caractérisation
    Son rôle: Comparer l'avant et l'après, chercher de nouvelles propriétés, relations, ou formes.
    Détecte ce qui "apparaît" (★).
    """
    def __init__(self):
        # Pour l'instant, on enveloppe la logique du Comparer v0.3.5
        self.comparer = Comparer()
        
    def analyze_trajectories(self, leaves: List[TrajectoryNode], initial_espace: Espace = None) -> Dict[str, Any]:
        """
        Analyse un lot de trajectoires terminales pour y déceler des émergences.
        """
        report = self.comparer.compare_nodes(leaves)
        
        # Simulation d'émergence coûteuse ou instable
        if initial_espace:
            espace = initial_espace
            is_couteux = any(b.caracteristiques.get("couteux", False) for b in espace.blocs_libres.values())
            is_instable = any(b.caracteristiques.get("instable", False) for b in espace.blocs_libres.values())
            
            for e in report.get("emergences", []):
                if is_couteux:
                    e["type"] += "_COUTEUX"
                if is_instable:
                    e["type"] += "_INSTABLE"
                    
        return report
