import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from meo.meo_engine import Espace
from meo.ontology import Bloc
from meo.transformations import LiaisonOp, CompositionOp
from meo.constraints import ConstraintProvider
from omx.orchestrator import OMXOrchestrator

class StrictAffinityConstraint(ConstraintProvider):
    """
    Univers A (Strict) :
    - '○' et '○' se repoussent.
    - '△' et '△' se repoussent.
    - '□' peut se lier avec tout le monde.
    """
    @property
    def name(self) -> str:
        return "MT02 Strict Rules (Univers A)"
        
    def evaluate(self, espace: Espace, transformation_data: dict) -> tuple[bool, str]:
        if transformation_data["operation"] == "LIAISON":
            b1_id = transformation_data["args"]["b1_id"]
            b2_id = transformation_data["args"]["b2_id"]
            
            b1 = espace.blocs_libres[b1_id]
            b2 = espace.blocs_libres[b2_id]
            
            if b1.forme == "○" and b2.forme == "○":
                return False, "Répulsion : ○ et ○"
                
            if b1.forme == "△" and b2.forme == "△":
                return False, "Répulsion : △ et △"
                
        return True, ""

class RelaxedAffinityConstraint(ConstraintProvider):
    """
    Univers B (Relaxé) :
    - '○' et '○' se repoussent.
    - '△' et '△' SONT AUTORISÉS (Loi relaxée).
    - '□' peut se lier avec tout le monde.
    """
    @property
    def name(self) -> str:
        return "MT02 Relaxed Rules (Univers B)"
        
    def evaluate(self, espace: Espace, transformation_data: dict) -> tuple[bool, str]:
        if transformation_data["operation"] == "LIAISON":
            b1_id = transformation_data["args"]["b1_id"]
            b2_id = transformation_data["args"]["b2_id"]
            
            b1 = espace.blocs_libres[b1_id]
            b2 = espace.blocs_libres[b2_id]
            
            if b1.forme == "○" and b2.forme == "○":
                return False, "Répulsion : ○ et ○"
                
            # La règle sur les △ est supprimée !
                
        return True, ""

def create_primordial_soup() -> Espace:
    espace = Espace()
    b1 = Bloc("B1", forme="○")
    b2 = Bloc("B2", forme="○")
    b3 = Bloc("B3", forme="△")
    b4 = Bloc("B4", forme="△")
    b5 = Bloc("B5", forme="□")
    
    espace.add_bloc_libre(b1)
    espace.add_bloc_libre(b2)
    espace.add_bloc_libre(b3)
    espace.add_bloc_libre(b4)
    espace.add_bloc_libre(b5)
    espace.global_properties["atp_pool"] = 5000
    return espace

def run_experiment(name: str, constraint: ConstraintProvider):
    print(f"\n{'='*50}")
    print(f"=== EXPÉRIENCE : {name} ===")
    print(f"{'='*50}")
    
    initial_espace = create_primordial_soup()
    
    omx = OMXOrchestrator()
    omx.register_transformation(LiaisonOp())
    omx.register_transformation(CompositionOp())
    omx.add_constraint(constraint)
    
    depth = 3
    print(f"\n[OMX] Lancement de l'exploration (Profondeur: {depth}) avec la loi '{constraint.name}'")
    report = omx.run_experiment_cycle(initial_espace, max_depth=depth)
    
    trajectories = report["trajectories"]
    print(f"\n=== SYNTHÈSE DES TRAJECTOIRES TERMINALES ({len(trajectories)} trouvées) ===")
    
    # Chercher spécifiquement si la structure B3+B4 a émergé
    b3_b4_count = 0
    
    for t in trajectories:
        path_str = t["path"]
        t_emergences = [e for e in report["emergences"] if e["path"] == t["id"]]
        
        for e in t_emergences:
            if "B3+B4" in e["description"]:
                b3_b4_count += 1
                
    print(f"\n🧪 RESULTAT SCIENTIFIQUE :")
    print(f"   - Nombre total de futurs possibles : {len(trajectories)}")
    print(f"   - Émergences de type 'B3+B4' (Triangle-Triangle) observées : {b3_b4_count}")
    
    if b3_b4_count > 0:
        print("   -> L'espace a généré de l'inédit grâce à la relaxation de la loi !")
    else:
        print("   -> La structure B3+B4 n'a pas pu se former.")

def test_mt02():
    print("\n=== TEST OdM-MT02 : CONTREFACTUALITÉ DES LOIS ===\n")
    
    # Même Bain Primordial pour les deux expériences
    print("Le Bain Primordial (E0) est rigoureusement identique pour les deux univers :")
    soup = create_primordial_soup()
    b_names = [f"{b.name}({b.forme})" for b in soup.blocs_libres.values()]
    print(f"Blocs présents : {', '.join(b_names)}")
    
    run_experiment("UNIVERS A (Contraintes Strictes)", StrictAffinityConstraint())
    run_experiment("UNIVERS B (Contraintes Relaxées)", RelaxedAffinityConstraint())

if __name__ == "__main__":
    test_mt02()
