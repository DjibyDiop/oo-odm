from typing import List, Dict, Any
from .ontology import Bloc, Liaison, Structure

class Element(Bloc):
    """
    Unité fondamentale de matière / connaissance.
    Hérite de Bloc pour assurer la continuité ontologique v0.2 -> v0.3.
    """
    def __init__(self, name: str, form: str = "○", properties: Dict[str, Any] = None):
        super().__init__(name, forme=form, caracteristiques=properties or {})
        self.energy = 0
        
    @property
    def form(self) -> str:
        return self.forme
        
    @form.setter
    def form(self, val: str):
        self.forme = val

class Espace:
    """
    Le conteneur topologique d'OdM.
    Contient des Blocs libres et des Structures complexes.
    """
    def __init__(self):
        self.blocs_libres: Dict[str, Bloc] = {}
        self.structures: List[Structure] = []
        self.global_properties: Dict[str, Any] = {}
        
    def add_bloc_libre(self, bloc: Bloc):
        self.blocs_libres[bloc.id] = bloc

    def add_element(self, element: Any):
        if isinstance(element, Bloc):
            self.add_bloc_libre(element)
        else:
            b = Bloc(element.name, forme=getattr(element, "form", "○"), caracteristiques=getattr(element, "properties", {}))
            b.id = element.id
            if hasattr(element, "energy"):
                b.caracteristiques["energy"] = element.energy
            self.add_bloc_libre(b)
        
    def add_structure(self, struct: Structure):
        self.structures.append(struct)

    @property
    def blocs(self) -> Dict[str, Bloc]:
        all_blocs = self.blocs_libres.copy()
        for struct in self.structures:
            all_blocs.update(struct.blocs)
        return all_blocs

    @property
    def relations(self) -> List[Liaison]:
        all_rel = []
        for struct in self.structures:
            all_rel.extend(struct.liaisons)
        return all_rel
        
    def clone(self) -> 'Espace':
        new_e = Espace()
        for b in self.blocs_libres.values():
            new_e.add_bloc_libre(b.clone())
        for s in self.structures:
            new_e.add_structure(s.clone())
        new_e.global_properties = self.global_properties.copy()
        return new_e

class OrganicExplorationEngine:
    """
    Moteur principal (MEO) qui explore l'Espace.
    """
    def __init__(self):
        self.espace = Espace()
        self.transformations: List[Any] = []
        self.history: List[Dict[str, Any]] = []

    @property
    def state(self) -> Espace:
        return self.espace
        
    def register_transformation(self, transformation: Any):
        self.transformations.append(transformation)

    def register_operation(self, operation: Any):
        self.register_transformation(operation)
        
    def get_possibilities(self) -> List[Dict[str, Any]]:
        """
        Génère les possibilités brutes en vérifiant uniquement les conditions
        structurelles/techniques des transformations.
        """
        possibilities = []
        for trans in self.transformations:
            t_possibilities = trans.check_conditions(self.espace)
            possibilities.extend(t_possibilities)
        return possibilities
