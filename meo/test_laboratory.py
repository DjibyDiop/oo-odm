import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.ontology import Bloc
from meo.meo_engine import OrganicExplorationEngine, Espace
from meo.transformations import LiaisonOp, CompositionOp
from meo.experiment import Experiment, ExplorationMode
from meo.comparer import Comparer

def test_laboratory():
    print("=== LABORATOIRE DES POSSIBILITÉS (Nouvelle Ontologie) ===")
    
    initial_espace = Espace()
    initial_espace.add_bloc_libre(Bloc("B1", forme="○"))
    initial_espace.add_bloc_libre(Bloc("B2", forme="△"))
    
    engine = OrganicExplorationEngine()
    engine.espace = initial_espace
    engine.register_transformation(LiaisonOp())
    engine.register_transformation(CompositionOp())
    
    exp = Experiment(engine, max_depth=2, mode=ExplorationMode.EXHAUSTIVE)
    exp.run()
    
    print("\n--- O-CHARACTERIZATION ---")
    comparer = Comparer()
    report = comparer.compare_nodes(exp.trajectories_leaves)
    
    for t in report["trajectories"]:
        print(f"[{t['id']}] {t['path']}")
        
    print("\nÉmergences détectées :")
    for e in report["emergences"]:
        print(f"  {e['type']} : {e['description']} (Sur chemin: {e['path']})")

if __name__ == "__main__":
    test_laboratory()
