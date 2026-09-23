import uuid
from typing import Dict, Any, List, Optional
from enum import Enum, auto

FORM_CIRCLE = "○"
FORM_TRIANGLE = "△"
FORM_SQUARE = "□"
FORM_STAR = "★"

class Bloc:
    """
    L'unité fondamentale de la matière OdM (Organique des Matières).
    Possède une forme (catégorie géométrique/comportementale) et des caractéristiques.
    
    Formes fondamentales :
      - ○ (Cercle)   : Centre, Contenant, Accumulateur de potentiel, Récepteur d'émergences.
      - △ (Triangle) : Porteur de données intrinsèques, orientation, asymétrie, direction.
      - □ (Carré)    : Limite, stabilité structurelle, résistance, cadre.
      - ★ (Étoile)   : Émergence, singularité, nouveauté irréductible, changement de paradigme.
    """
    def __init__(self, name: str, forme: str = FORM_CIRCLE, caracteristiques: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.forme = forme
        self.caracteristiques = caracteristiques or {}
        
        # Propriétés géométriques intrinsèques
        self.orientation = self.caracteristiques.get("orientation", 0.0)
        self.asymetrie = self.caracteristiques.get("asymetrie", (forme == FORM_TRIANGLE))
        self.stabilite = self.caracteristiques.get("stabilite", 1.0 if forme == FORM_SQUARE else 0.5)
        self.potentiel = self.caracteristiques.get("potentiel", 100.0 if forme == FORM_CIRCLE else 50.0)
        self.is_emergent = self.caracteristiques.get("is_emergent", (forme == FORM_STAR))
        
        # Structure de contenance récursive
        self.contenu: List['Bloc'] = []
        
        # Journal d'évolution historique
        self.historique: List[Dict[str, Any]] = [
            {"event": "CREATION", "forme": self.forme, "caracteristiques": self.caracteristiques.copy()}
        ]
        
    def clone(self) -> 'Bloc':
        new_b = Bloc(self.name, self.forme, self.caracteristiques.copy())
        new_b.id = self.id
        new_b.orientation = self.orientation
        new_b.asymetrie = self.asymetrie
        new_b.stabilite = self.stabilite
        new_b.potentiel = self.potentiel
        new_b.is_emergent = self.is_emergent
        new_b.contenu = [c.clone() for c in self.contenu]
        new_b.historique = list(self.historique)
        return new_b

    def record_evolution(self, operation: str, details: Dict[str, Any]):
        """Enregistre le devenir du bloc sans écraser son passé."""
        self.historique.append({
            "operation": operation,
            "details": details,
            "state_snapshot": self.caracteristiques.copy()
        })

    def signature(self) -> str:
        return f"{self.forme}({self.name})"

class Liaison:
    """
    Une connexion relationnelle entre deux Blocs.
    """
    def __init__(self, source_id: str, target_id: str, nature: str = "faible", oriente: bool = False, force: float = 1.0):
        self.id = str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.nature = nature
        self.oriente = oriente
        self.force = force
        self.active = True
        
    def clone(self) -> 'Liaison':
        new_l = Liaison(self.source_id, self.target_id, self.nature, self.oriente, self.force)
        new_l.id = self.id
        new_l.active = self.active
        return new_l

class Structure:
    """
    Une combinaison topologique de Blocs liés formant une organisation d'ordre supérieur.
    """
    def __init__(self, name: str = "S0"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.blocs: Dict[str, Bloc] = {}
        self.liaisons: List[Liaison] = []
        
    def add_bloc(self, bloc: Bloc):
        self.blocs[bloc.id] = bloc
        
    def add_liaison(self, liaison: Liaison):
        self.liaisons.append(liaison)
        
    def topologie(self) -> str:
        n_b = len(self.blocs)
        n_l = len(self.liaisons)
        if n_b >= 3 and n_l >= n_b:
            topo = "cycle"
        elif n_b >= 3 and n_l == n_b - 1:
            topo = "arbre/etoile"
        elif n_b == 2 and n_l >= 1:
            topo = "paire"
        else:
            topo = "complexe"
        return f"Structure(blocs={n_b}, liaisons={n_l}, topo={topo})"
        
    def capacites_structurelles(self) -> List[str]:
        caps = []
        if len(self.blocs) < 2:
            caps.append("inerte")
        else:
            caps.append("active")
            # Présence de triangle = directionnalité
            if any(b.forme == FORM_TRIANGLE for b in self.blocs.values()):
                caps.append("directionnel")
            # Présence de cercle = accumulation
            if any(b.forme == FORM_CIRCLE for b in self.blocs.values()):
                caps.append("accumulateur")
            # Présence de carré = stabilité
            if any(b.forme == FORM_SQUARE for b in self.blocs.values()):
                caps.append("protecteur")
            # Présence d'étoile = singularité
            if any(b.forme == FORM_STAR for b in self.blocs.values()):
                caps.append("singulier")
        return caps
        
    def clone(self) -> 'Structure':
        new_s = Structure(self.name)
        new_s.id = self.id
        for b in self.blocs.values():
            new_s.add_bloc(b.clone())
        for l in self.liaisons:
            new_s.add_liaison(l.clone())
        return new_s

class EmergenceType(Enum):
    NOUVELLE_STRUCTURE = auto()
    NOUVELLE_PROPRIETE = auto()
    NOUVELLE_CAPACITE = auto()
    NOUVELLE_RELATION = auto()
    NOUVEAU_COMPORTEMENT = auto()
    SINGULARITE_ETOILE = auto()

class EmergenceReport:
    """
    Rapport d'émergence (★ / [*]) lorsqu'une nouveauté structurelle irréductible est identifiée.
    """
    def __init__(self, type: EmergenceType, description: str, source_path: str):
        self.type = type
        self.description = description
        self.source_path = source_path
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": f"[*] {self.type.name}",
            "description": self.description,
            "path": self.source_path
        }
