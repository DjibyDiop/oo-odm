from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import copy
from .meo_engine import Espace
from .ontology import Bloc, Liaison, Structure, FORM_CIRCLE, FORM_TRIANGLE, FORM_SQUARE, FORM_STAR

class Transformation(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def execute(self, espace: Espace, **kwargs) -> Espace:
        pass

class LiaisonOp(Transformation):
    """
    1 — LIAISON:
    Connecte deux Blocs libres pour former ou enrichir une organisation/structure.
    """
    @property
    def name(self) -> str:
        return "LIAISON"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        libres_ids = list(espace.blocs_libres.keys())
        
        for i in range(len(libres_ids)):
            for j in range(i+1, len(libres_ids)):
                possibilities.append({
                    "operation": self.name,
                    "args": {"b1_id": libres_ids[i], "b2_id": libres_ids[j]},
                    "atp_cost": 50
                })
        return possibilities
        
    def execute(self, espace: Espace, b1_id: str, b2_id: str) -> Espace:
        new_espace = espace.clone()
        
        b1 = new_espace.blocs_libres.pop(b1_id)
        b2 = new_espace.blocs_libres.pop(b2_id)
        
        b1.record_evolution("LIAISON", {"partner": b2.name, "nature": "liaison_libre"})
        b2.record_evolution("LIAISON", {"partner": b1.name, "nature": "liaison_libre"})
        
        struct = Structure(f"S({b1.name}-{b2.name})")
        struct.add_bloc(b1)
        struct.add_bloc(b2)
        struct.add_liaison(Liaison(b1.id, b2.id))
        
        new_espace.add_structure(struct)
        return new_espace

class CompositionOp(Transformation):
    """
    4 — COMPOSITION:
    Synthétise structurellement tous les Blocs d'une Structure pour créer un super-Bloc d'ordre supérieur,
    qui redevient un Bloc libre prêt à interagir.
    """
    @property
    def name(self) -> str:
        return "COMPOSITION"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        for struct in espace.structures:
            if len(struct.blocs) >= 2:
                possibilities.append({
                    "operation": self.name,
                    "args": {"struct_id": struct.id},
                    "atp_cost": 200
                })
        return possibilities
        
    def execute(self, espace: Espace, struct_id: str) -> Espace:
        new_espace = espace.clone()
        
        struct = next((s for s in new_espace.structures if s.id == struct_id), None)
        if not struct:
            return new_espace
            
        new_espace.structures.remove(struct)
        
        b_names = [b.name for b in struct.blocs.values()]
        # Calcul des propriétés composées
        total_energy = sum(b.caracteristiques.get("energy", 0) for b in struct.blocs.values())
        is_novel = any(b.forme == FORM_STAR for b in struct.blocs.values()) or len(b_names) >= 3
        
        new_props = {
            "composed_from": struct.name,
            "energy": total_energy,
            "is_emergent": is_novel
        }
        
        # Forme résultante : Étoile si singulier, sinon Carré (structure stable)
        resulting_form = FORM_STAR if is_novel else FORM_SQUARE
        super_bloc = Bloc("+".join(b_names), forme=resulting_form, caracteristiques=new_props)
        super_bloc.record_evolution("COMPOSITION", {"source_structure": struct.name, "constituents": b_names})
        
        new_espace.add_bloc_libre(super_bloc)
        return new_espace

class TransformationOp(Transformation):
    """
    3 — TRANSFORMATION:
    Modifie les propriétés internes, l'état thermique, l'énergie ou la forme d'un bloc sans briser son identité.
    """
    @property
    def name(self) -> str:
        return "TRANSFORMATION"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        for b_id, bloc in espace.blocs_libres.items():
            possibilities.append({
                "operation": self.name,
                "args": {"bloc_id": b_id, "delta_energy": 25},
                "atp_cost": 20
            })
        return possibilities
        
    def execute(self, espace: Espace, bloc_id: str, delta_energy: int = 25, new_forme: Optional[str] = None, delta_state: Optional[Dict[str, Any]] = None) -> Espace:
        new_espace = espace.clone()
        bloc = new_espace.blocs.get(bloc_id)
        if bloc:
            prev_snapshot = bloc.caracteristiques.copy()
            cur_energy = bloc.caracteristiques.get("energy", 0) + delta_energy
            bloc.caracteristiques["energy"] = cur_energy
            
            if delta_state:
                bloc.caracteristiques.update(delta_state)
                
            if new_forme:
                bloc.forme = new_forme
                
            bloc.record_evolution("TRANSFORMATION", {
                "before": prev_snapshot,
                "after": bloc.caracteristiques.copy(),
                "delta_energy": delta_energy
            })
        return new_espace

class ContenirOp(Transformation):
    """
    5 — CONTENIR:
    Englobe un bloc au sein d'un autre sans détruire son identité (contenance récursive).
    """
    @property
    def name(self) -> str:
        return "CONTENIR"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        libres = list(espace.blocs_libres.values())
        for container in libres:
            # Les cercles (○) et carrés (□) sont d'excellents contenants
            if container.forme in [FORM_CIRCLE, FORM_SQUARE]:
                for contained in libres:
                    if contained.id != container.id:
                        possibilities.append({
                            "operation": self.name,
                            "args": {"container_id": container.id, "contained_id": contained.id},
                            "atp_cost": 45
                        })
        return possibilities
        
    def execute(self, espace: Espace, container_id: str, contained_id: str) -> Espace:
        new_espace = espace.clone()
        if container_id in new_espace.blocs_libres and contained_id in new_espace.blocs_libres:
            container = new_espace.blocs_libres[container_id]
            contained = new_espace.blocs_libres.pop(contained_id)
            
            container.contenu.append(contained)
            container.record_evolution("CONTENIR", {"contained_bloc": contained.signature()})
        return new_espace

class CaracterisationOp(Transformation):
    """
    7 — CARACTÉRISATION (KAR):
    Observation non destructive mesurant l'état réel, la distribution d'énergie et l'indice d'émergence.
    """
    @property
    def name(self) -> str:
        return "CARACTERISATION"
        
    def check_conditions(self, espace: Espace) -> List[Dict[str, Any]]:
        possibilities = []
        for b_id in espace.blocs:
            possibilities.append({
                "operation": self.name,
                "args": {"bloc_id": b_id},
                "atp_cost": 10
            })
        return possibilities
        
    def execute(self, espace: Espace, bloc_id: str) -> Espace:
        # Non destructif : retourne un clone inchangé avec rapport dans global_properties
        new_espace = espace.clone()
        target = new_espace.blocs.get(bloc_id)
        if target:
            new_espace.global_properties[f"kar_{bloc_id}"] = {
                "name": target.name,
                "forme": target.forme,
                "caracteristiques": copy.deepcopy(target.caracteristiques),
                "contenu_count": len(target.contenu),
                "historique_depth": len(target.historique)
            }
        return new_espace
