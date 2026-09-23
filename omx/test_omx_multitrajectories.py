import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.ontology import Bloc
from meo.meo_engine import Espace
from meo.transformations import LiaisonOp, CompositionOp
from meo.constraints import ConstraintProvider
from omx.orchestrator import OMXOrchestrator

class AffinityConstraint(ConstraintProvider):
    """
    Règle O-D+ : Restreint les liaisons possibles pour simuler une affinité
    chimique/topologique, et ainsi éviter l'explosion combinatoire.
    - '○' ne peut se lier qu'avec '△' ou '□'.
    - '△' ne peut se lier qu'avec '○' ou '□'.
    - '□' peut se lier avec tout le monde.
    """
    @property
    def name(self) -> str:
        return "MT01 Affinity Rules"
        
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

def test_multitrajectories():
    print("=== TEST OdM-MT01 : EXPLORATION MULTI-TRAJECTOIRES ===")
    print("[OMX] Initialisation du Laboratoire avec 5 Blocs (Le Bain Primordial)")
    
    initial_espace = Espace()
    
    # Création du pool de blocs
    blocs_initiaux = [
        Bloc("B1", forme="○", caracteristiques={"nature": "fluide"}),
        Bloc("B2", forme="○", caracteristiques={"nature": "fluide"}),
        Bloc("B3", forme="△", caracteristiques={"nature": "rigide"}),
        Bloc("B4", forme="△", caracteristiques={"nature": "rigide"}),
        Bloc("B5", forme="□", caracteristiques={"nature": "catalyseur"})
    ]
    
    for b in blocs_initiaux:
        initial_espace.add_bloc_libre(b)
        
    initial_espace.global_properties["atp_pool"] = 5000
    
    print(f"Blocs présents : {', '.join([b.name + '(' + b.forme + ')' for b in blocs_initiaux])}")
    
    # Orchestrator
    omx = OMXOrchestrator()
    omx.register_transformation(LiaisonOp())
    omx.register_transformation(CompositionOp())
    
    # Application de la règle (La Constitution agit via D+)
    omx.add_constraint(AffinityConstraint())
    
    depth = 3
    print(f"\n[OMX] Lancement de l'exploration (Profondeur: {depth})")
    
    report = omx.run_experiment_cycle(initial_espace, max_depth=depth)
    
    print(f"\n=== SYNTHÈSE DES TRAJECTOIRES TERMINALES ({len(report['trajectories'])} trouvées) ===")
    
    # On affiche juste les 5 premières et les 5 dernières pour ne pas spammer
    trajectories = report["trajectories"]
    display_limit = 10
    
    for i, t in enumerate(trajectories):
        if i < 5 or i >= len(trajectories) - 5:
            # Formatage du chemin
            path_str = t["path"]
            print(f"[{t['id']}] {path_str}")
            print(f"    Signature finale: {t['signature']}")
            
            # Afficher les émergences s'il y en a eu sur cette trajectoire
            t_emergences = [e for e in report["emergences"] if e["path"] == t["id"]]
            if t_emergences:
                print(f"    ⭐ Émergences détectées :")
                for e in t_emergences:
                    print(f"       - {e['type']} : {e['description']}")
        elif i == 5:
            print(f"    ... ({len(trajectories) - 10} trajectoires masquées) ...")

    print("\n[O-DISCOVERY] Expérience terminée avec succès.")
    
if __name__ == "__main__":
    test_multitrajectories()
