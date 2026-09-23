"""
OO-ODM — Modélisation 002 : L'Épreuve du Vide
Spécification exacte issue de plan.md (L1953-2050).
Le protocole des 5 épreuves fondamentales dans le vide :
  1. L'Épreuve de l'Existence (Stabilité intrinsèque du bloc seul)
  2. L'Épreuve de la Rencontre (Capacité de liaison spontanée)
  3. L'Épreuve de la Résistance (Tenue sous contrainte de rupture)
  4. L'Épreuve de l'Annihilation (Conservation sous division / choc)
  5. L'Épreuve de la Complexité Asymétrique (Moment directionnel ○ + △)
"""
from typing import Dict, Any, List
from .ontology import Bloc, FORM_CIRCLE, FORM_TRIANGLE, FORM_SQUARE, FORM_STAR
from .meo_engine import Espace
from .operations import LiaisonOp, RuptureOp, DivisionOp

class Model002EpreuveDuVide:
    def __init__(self):
        self.results: Dict[str, Any] = {}
        
    def run_all_epreuves(self) -> Dict[str, bool]:
        # --- 1. Épreuve de l'Existence ---
        esp1 = Espace()
        b1 = Bloc("B1", forme=FORM_CIRCLE, caracteristiques={"energy": 100})
        esp1.add_bloc_libre(b1)
        # Vérifie que le bloc existe et conserve son énergie sans dérive
        epreuve1_passed = (len(esp1.blocs_libres) == 1 and esp1.blocs_libres[b1.id].caracteristiques["energy"] == 100)
        self.results["1_existence"] = epreuve1_passed
        
        # --- 2. Épreuve de la Rencontre ---
        esp2 = Espace()
        b1 = Bloc("B1", forme=FORM_CIRCLE)
        b2 = Bloc("B2", forme=FORM_SQUARE)
        esp2.add_bloc_libre(b1)
        esp2.add_bloc_libre(b2)
        
        liaison_op = LiaisonOp()
        esp2 = liaison_op.execute(esp2, b1.id, b2.id)
        epreuve2_passed = (len(esp2.structures) == 1 and len(esp2.structures[0].blocs) == 2)
        self.results["2_rencontre"] = epreuve2_passed
        
        # --- 3. Épreuve de la Résistance ---
        rupture_op = RuptureOp()
        struct_id = esp2.structures[0].id
        liaison_id = esp2.structures[0].liaisons[0].id
        esp3 = rupture_op.execute(esp2, struct_id, liaison_id)
        # Doit avoir libéré les blocs sans perte de substance
        epreuve3_passed = (len(esp3.structures) == 0 and len(esp3.blocs_libres) == 2)
        self.results["3_resistance"] = epreuve3_passed
        
        # --- 4. Épreuve de l'Annihilation / Division ---
        esp4 = Espace()
        b_parent = Bloc("MatiereSource", forme=FORM_SQUARE, caracteristiques={"energy": 120})
        esp4.add_bloc_libre(b_parent)
        
        div_op = DivisionOp()
        esp4 = div_op.execute(esp4, b_parent.id, mode="partition")
        # Doit produire 2 enfants dont la somme des énergies est égale à 120
        total_e = sum(b.caracteristiques["energy"] for b in esp4.blocs_libres.values())
        epreuve4_passed = (len(esp4.blocs_libres) == 2 and total_e == 120)
        self.results["4_annihilation"] = epreuve4_passed
        
        # --- 5. Épreuve de la Complexité Asymétrique ---
        esp5 = Espace()
        cercle = Bloc("CercleSym", forme=FORM_CIRCLE, caracteristiques={"energy": 50})
        triangle = Bloc("TriangleVect", forme=FORM_TRIANGLE, caracteristiques={"angle": 90.0, "asymetrie": True})
        esp5.add_bloc_libre(cercle)
        esp5.add_bloc_libre(triangle)
        esp5 = liaison_op.execute(esp5, cercle.id, triangle.id)
        
        struct_asym = esp5.structures[0]
        capacites = struct_asym.capacites_structurelles()
        epreuve5_passed = ("directionnel" in capacites and "accumulateur" in capacites)
        self.results["5_complexite_asymetrique"] = epreuve5_passed
        
        return self.results
