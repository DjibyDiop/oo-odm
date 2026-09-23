import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.ontology import Bloc
from meo.meo_engine import Espace
from meo.transformations import LiaisonOp, CompositionOp
from omx.orchestrator import OMXOrchestrator

def test_omx_architecture():
    print("=== TEST ARCHITECTURE OMX (Topologie OdM) ===")
    
    # 1. Initialisation de l'Espace avec Blocs libres
    initial_espace = Espace()
    b1 = Bloc("B1", forme="○", caracteristiques={"nature": "absorbant", "volume": 1})
    b2 = Bloc("B2", forme="△", caracteristiques={"nature": "neutre", "volume": 1})
    initial_espace.add_bloc_libre(b1)
    initial_espace.add_bloc_libre(b2)
    initial_espace.global_properties["atp_pool"] = 1000
    
    # 2. Initialisation d'OMX
    omx = OMXOrchestrator()
    
    # 3. Enregistrement de la physique (O-DYNAMICS)
    omx.register_transformation(LiaisonOp())
    omx.register_transformation(CompositionOp())
    
    # 4. Exécution
    report = omx.run_experiment_cycle(initial_espace, max_depth=2)
    
    print("\n=== RAPPORT D'EXPÉRIENCE (RÉSUMÉ) ===")
    for t in report["trajectories"]:
        print(f"[{t['id']}] {t['path']} -> Signature: {t['signature']}")
        
    print("\n[OMX] Le cycle est terminé. Le système est en attente d'une nouvelle consigne.")

if __name__ == "__main__":
    test_omx_architecture()
