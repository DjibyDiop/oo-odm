"""
OO-ODM — Modélisation 001 : L'Absorption
Spécification exacte issue de plan.md (L1367-1450).
Phénomène élémentaire d'absorption d'énergie entre une source et un récepteur.
"""
from typing import Dict, Any
from .ontology import Bloc, FORM_CIRCLE, FORM_SQUARE, FORM_STAR, EmergenceReport, EmergenceType
from .meo_engine import Espace
from .operations import LiaisonOp, TransformationOp, CaracterisationOp

class Model001Absorption:
    """
    Modélisation 001 :
    1. État initial (L'Espace) : ○A (Énergie: 100) et □B (Récepteur: 0)
    2. L'Événement (LIAISON + Absorption progressive)
    3. Le Bilan (Conservation et transfert d'état)
    4. L'Émergence d'une règle (La Connaissance : activation de B en état ★ si seuil atteint)
    """
    def __init__(self, initial_energy_a: int = 100):
        self.espace = Espace()
        self.bloc_a = Bloc("SourceA", forme=FORM_CIRCLE, caracteristiques={"energy": initial_energy_a, "flux": 20})
        self.bloc_b = Bloc("RecepteurB", forme=FORM_SQUARE, caracteristiques={"energy": 0, "active": False})
        
        self.espace.add_bloc_libre(self.bloc_a)
        self.espace.add_bloc_libre(self.bloc_b)
        
        self.liaison_op = LiaisonOp()
        self.trans_op = TransformationOp()
        self.kar_op = CaracterisationOp()
        
    def step_interaction(self, transfer_amount: int = 40) -> Dict[str, Any]:
        """Effectue le transfert énergétique et vérifie l'émergence d'état."""
        # 1. Liaison si pas encore liée
        if len(self.espace.structures) == 0:
            self.espace = self.liaison_op.execute(self.espace, self.bloc_a.id, self.bloc_b.id)
            
        # 2. Transfert d'énergie de A vers B
        struct = self.espace.structures[0]
        a = struct.blocs[self.bloc_a.id]
        b = struct.blocs[self.bloc_b.id]
        
        actual_transfer = min(transfer_amount, a.caracteristiques["energy"])
        a.caracteristiques["energy"] -= actual_transfer
        b.caracteristiques["energy"] += actual_transfer
        
        # 3. Émergence de nouvelle règle si B franchit le seuil critique (>= 50)
        emergence_detected = False
        if b.caracteristiques["energy"] >= 50 and not b.caracteristiques["active"]:
            b.caracteristiques["active"] = True
            b.forme = FORM_STAR # Émergence d'activation
            emergence_detected = True
            report = EmergenceReport(
                EmergenceType.NOUVELLE_PROPRIETE,
                f"Le récepteur {b.name} est activé en état singulier ★ par saturation énergétique.",
                "Model001.Absorption"
            )
            self.espace.global_properties["emergence"] = report.to_dict()
            
        return {
            "energy_a": a.caracteristiques["energy"],
            "energy_b": b.caracteristiques["energy"],
            "b_active": b.caracteristiques["active"],
            "emergence": emergence_detected
        }

    def run_full(self) -> Dict[str, Any]:
        step1 = self.step_interaction(30)
        step2 = self.step_interaction(40)
        return {
            "step1": step1,
            "step2": step2,
            "final_espace": self.espace
        }
