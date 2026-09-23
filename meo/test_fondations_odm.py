import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.ontology import Bloc
from meo.meo_engine import OrganicExplorationEngine, Espace
from meo.transformations import LiaisonOp, CompositionOp
from meo.experiment import Experiment, ExplorationMode

def test_fondations():
    print("=== TEST FONDATIONS OdM (Nouvelle Ontologie) ===")
    
    # 1. État initial (Espace)
    initial_espace = Espace()
    initial_espace.add_bloc_libre(Bloc("B1", forme="○"))
    initial_espace.add_bloc_libre(Bloc("B2", forme="△"))
    
    # 2. Moteur d'exploration
    engine = OrganicExplorationEngine()
    engine.espace = initial_espace
    engine.register_transformation(LiaisonOp())
    engine.register_transformation(CompositionOp())
    
    # 3. Expérience (Profondeur 2)
    exp = Experiment(engine, max_depth=2, mode=ExplorationMode.EXHAUSTIVE)
    exp.run()
    
    # Affichage des feuilles
    print(f"\nTrajectoires générées : {len(exp.trajectories_leaves)}")
    for i, leaf in enumerate(exp.trajectories_leaves):
        path_str = " -> ".join([step["operation"] for step in leaf.path])
        print(f"Trajectoire {i}: {path_str}")
        print(f"  Structures à la fin: {len(leaf.espace.structures)}")
        print(f"  Blocs libres à la fin: {len(leaf.espace.blocs_libres)}")

if __name__ == "__main__":
    test_fondations()
