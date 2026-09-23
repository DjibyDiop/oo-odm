"""
OO-ODM — Modélisation 003 : La Cire qui fond
Spécification exacte issue de plan.md (L2485-2650).
Transition thermodynamique de phase :
  - État initial T < T_fusion : structure rigide solide de carrés □ fortement liés.
  - Chauffage continu (injection d'énergie thermique).
  - Au-delà du seuil critique (T >= 60°C) : rupture des liaisons rigides,
    transformation géométrique □ -> ○ (gouttes fluides mobiles) et réorganisation en agrégats liquides.
"""
from typing import Dict, Any, List
from .ontology import Bloc, Liaison, Structure, FORM_CIRCLE, FORM_SQUARE, EmergenceReport, EmergenceType
from .meo_engine import Espace
from .operations import LiaisonOp, RuptureOp, TransformationOp

class Model003CireQuiFond:
    def __init__(self, initial_temp: float = 20.0, seuil_fusion: float = 60.0):
        self.temp = initial_temp
        self.seuil_fusion = seuil_fusion
        self.phase = "SOLIDE"
        self.espace = Espace()
        
        # Création du réseau cristallin solide initial (3 blocs de cire □ liés)
        b1 = Bloc("Cire_1", forme=FORM_SQUARE, caracteristiques={"temp": self.temp, "viscosite": 100.0})
        b2 = Bloc("Cire_2", forme=FORM_SQUARE, caracteristiques={"temp": self.temp, "viscosite": 100.0})
        b3 = Bloc("Cire_3", forme=FORM_SQUARE, caracteristiques={"temp": self.temp, "viscosite": 100.0})
        
        self.espace.add_bloc_libre(b1)
        self.espace.add_bloc_libre(b2)
        self.espace.add_bloc_libre(b3)
        
        # Liaison en chaîne rigide
        liaison_op = LiaisonOp()
        self.espace = liaison_op.execute(self.espace, b1.id, b2.id)
        # On attache aussi b3
        struct = self.espace.structures[0]
        b3_ref = self.espace.blocs_libres.pop(b3.id)
        struct.add_bloc(b3_ref)
        struct.add_liaison(Liaison(b2.id, b3_ref.id, nature="rigide", force=5.0))
        
    def heat_step(self, delta_t: float = 25.0) -> Dict[str, Any]:
        """Injecte de la chaleur et déclenche la transition de phase si seuil franchi."""
        self.temp += delta_t
        transition_occurred = False
        
        # Mise à jour de la température de tous les blocs
        for b in self.espace.blocs.values():
            b.caracteristiques["temp"] = self.temp
            
        if self.temp >= self.seuil_fusion and self.phase == "SOLIDE":
            self.phase = "LIQUIDE"
            transition_occurred = True
            
            # Récupérer d'abord tous les blocs avant de dissoudre les structures
            all_blocs = list(self.espace.blocs.values())
            
            # Dissolution des structures rigides
            self.espace.structures.clear()
            self.espace.blocs_libres.clear()
            
            # Métamorphose morphologique : les carrés □ deviennent des gouttes rondes ○
            for b in all_blocs:
                b.forme = FORM_CIRCLE
                b.caracteristiques["viscosite"] = 5.0 # Forte fluidité
                b.record_evolution("TRANSITION_PHASE_FUSION", {"temp": self.temp, "nouvelle_forme": FORM_CIRCLE})
                self.espace.add_bloc_libre(b)
                
            # Rapport d'émergence thermodynamique
            report = EmergenceReport(
                EmergenceType.NOUVEAU_COMPORTEMENT,
                f"Transition de phase Solide -> Liquide franchie à T={self.temp}°C. Métamorphose □ -> ○.",
                "Model003.CireQuiFond"
            )
            self.espace.global_properties["phase_transition"] = report.to_dict()
            
        return {
            "temperature": self.temp,
            "phase": self.phase,
            "transition": transition_occurred,
            "formes": [b.forme for b in self.espace.blocs.values()]
        }

    def run_simulation(self) -> List[Dict[str, Any]]:
        history = []
        # Chauffage progressif : 20 -> 45 -> 70 -> 95
        history.append(self.heat_step(25.0)) # 45°C (reste solide)
        history.append(self.heat_step(25.0)) # 70°C (fond en liquide ○)
        history.append(self.heat_step(25.0)) # 95°C (liquide chaud)
        return history
