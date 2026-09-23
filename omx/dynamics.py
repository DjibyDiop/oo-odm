from typing import List, Dict, Any
import sys
import os

# Ajout du chemin parent pour importer depuis meo/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.meo_engine import Espace
from meo.transformations import Transformation

class DynamicsEngine:
    """
    O-DYNAMICS: Moteur de Dynamique
    Son rôle: Faire évoluer la matière en exécutant les transformations formelles.
    Il ne choisit pas quoi exécuter, il exécute la physique d'OdM.
    """
    def __init__(self):
        self.transformations: List[Transformation] = []
        
    def register_transformation(self, transformation: Transformation):
        self.transformations.append(transformation)
        
    def get_raw_possibilities(self, espace: Espace) -> List[Dict[str, Any]]:
        """
        Déduit toutes les transformations structurellement possibles depuis cet Espace.
        """
        possibilities = []
        for trans in self.transformations:
            t_possibilities = trans.check_conditions(espace)
            possibilities.extend(t_possibilities)
        return possibilities

    def apply_transformation(self, espace: Espace, possibility: Dict[str, Any]) -> Espace:
        """
        Applique une transformation et retourne le nouvel Espace généré.
        Prend la possibilité complète telle que retournée par get_raw_possibilities.
        """
        next_espace = espace.clone()
        trans_name = possibility["operation"]
        args = possibility["args"]
        
        trans_obj = next(t for t in self.transformations if t.name == trans_name)
        next_espace = trans_obj.execute(next_espace, **args)
        
        cost = possibility.get("atp_cost", 0)
        next_espace.global_properties["atp_pool"] -= cost
        
        return next_espace
