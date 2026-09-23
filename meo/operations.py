from typing import List, Dict, Any, Optional
from .transformations import (
    Transformation,
    LiaisonOp,
    CompositionOp,
    TransformationOp,
    ContenirOp,
    CaracterisationOp
)
from .ontology import Bloc, Liaison, Structure, FORM_CIRCLE, FORM_TRIANGLE, FORM_SQUARE, FORM_STAR
from .meo_engine import Espace

class RuptureOp(Transformation):
    """
    2 — RUPTURE:
    Rompt une liaison active dans une structure. Libère les blocs si la structure est disloquée.
    """
    @property
    def name(self) -> str:
        return "RUPTURE"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        for struct in espace.structures:
            for l in struct.liaisons:
                if l.active:
                    possibilities.append({
                        "operation": self.name,
                        "args": {"struct_id": struct.id, "liaison_id": l.id},
                        "atp_cost": 30
                    })
        return possibilities
        
    def execute(self, espace: Espace, struct_id: str, liaison_id: str) -> Espace:
        new_espace = espace.clone()
        struct = next((s for s in new_espace.structures if s.id == struct_id), None)
        if not struct:
            return new_espace
            
        target_liaison = next((l for l in struct.liaisons if l.id == liaison_id), None)
        if target_liaison:
            target_liaison.active = False
            struct.liaisons = [l for l in struct.liaisons if l.id != liaison_id]
            
            # Si plus aucune liaison active, libérer les blocs dans l'espace
            if len(struct.liaisons) == 0:
                new_espace.structures.remove(struct)
                for bloc in struct.blocs.values():
                    bloc.record_evolution("RUPTURE_DISSOLUTION", {"structure": struct.name})
                    new_espace.add_bloc_libre(bloc)
            else:
                for bloc in struct.blocs.values():
                    bloc.record_evolution("RUPTURE_PARTIELLE", {"liaison_id": liaison_id})
                    
        return new_espace

class DivisionOp(Transformation):
    """
    6 — DIVISION:
    Scinde un bloc en 2+ sous-unités selon trois modes fondamentaux (plan.md):
      1. Partition : divise la masse/énergie entre les fragments.
      2. Duplication : réplique le bloc à l'identique (isomorphisme).
      3. Différenciation : produit deux descendants asymétriques spécialisés.
    """
    @property
    def name(self) -> str:
        return "DIVISION"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        for b_id, bloc in espace.blocs_libres.items():
            possibilities.append({
                "operation": self.name,
                "args": {"bloc_id": b_id, "mode": "partition"},
                "atp_cost": 40
            })
        return possibilities
        
    def execute(self, espace: Espace, bloc_id: str, mode: str = "partition") -> Espace:
        new_espace = espace.clone()
        if bloc_id in new_espace.blocs_libres:
            orig = new_espace.blocs_libres.pop(bloc_id)
            orig_energy = orig.caracteristiques.get("energy", 100)
            
            if mode == "partition":
                # Mode 1 : Partition
                e_half = orig_energy // 2
                props1 = orig.caracteristiques.copy()
                props2 = orig.caracteristiques.copy()
                props1["energy"] = e_half
                props2["energy"] = orig_energy - e_half
                
                b1 = Bloc(f"{orig.name}_1", forme=orig.forme, caracteristiques=props1)
                b2 = Bloc(f"{orig.name}_2", forme=orig.forme, caracteristiques=props2)
                
            elif mode == "duplication":
                # Mode 2 : Duplication
                b1 = Bloc(f"{orig.name}_clone1", forme=orig.forme, caracteristiques=orig.caracteristiques.copy())
                b2 = Bloc(f"{orig.name}_clone2", forme=orig.forme, caracteristiques=orig.caracteristiques.copy())
                
            elif mode == "differentiation":
                # Mode 3 : Différenciation (○ donne un Triangle orienté et un Carré stable)
                props_dir = orig.caracteristiques.copy()
                props_dir["angle"] = 45.0
                props_stab = orig.caracteristiques.copy()
                props_stab["stabilite"] = 1.0
                
                b1 = Bloc(f"{orig.name}_vect", forme=FORM_TRIANGLE, caracteristiques=props_dir)
                b2 = Bloc(f"{orig.name}_base", forme=FORM_SQUARE, caracteristiques=props_stab)
            else:
                # Défaut
                b1 = Bloc(f"{orig.name}_1", forme=orig.forme, caracteristiques=orig.caracteristiques.copy())
                b2 = Bloc(f"{orig.name}_2", forme=orig.forme, caracteristiques=orig.caracteristiques.copy())
                
            b1.record_evolution("DIVISION_CHILD", {"parent": orig.name, "mode": mode})
            b2.record_evolution("DIVISION_CHILD", {"parent": orig.name, "mode": mode})
            
            new_espace.add_bloc_libre(b1)
            new_espace.add_bloc_libre(b2)
            
        return new_espace

# Exportation exhaustive des 7 Opérations Fondamentales de l'OdM
__all__ = [
    "LiaisonOp",
    "RuptureOp",
    "TransformationOp",
    "CompositionOp",
    "ContenirOp",
    "DivisionOp",
    "CaracterisationOp"
]
