import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meo.meo_engine import Element, OrganicExplorationEngine
from meo.operations import LiaisonOp, RuptureOp, DivisionOp
from meo.experiment import Experiment, ExplorationMode
from oo_adapter import OOConstitutionalProvider

def test_meo_v03():
    # Initialisation du moteur avec le ConstraintProvider de OO
    oo_provider = OOConstitutionalProvider()
    engine = OrganicExplorationEngine()
    
    # Enregistrement des opérations
    engine.register_operation(LiaisonOp())
    engine.register_operation(RuptureOp())
    engine.register_operation(DivisionOp())
    
    # Création du monde expérimental initial (OO)
    e1 = Element("Noyau")
    e1.energy = 50
    e2 = Element("Mitochondrie")
    e2.energy = 100
    e3 = Element("Membrane")
    
    engine.state.add_element(e1)
    engine.state.add_element(e2)
    engine.state.add_element(e3)
    
    # Définition des propriétés globales (Constitution)
    engine.state.global_properties["atp_pool"] = 300  # Pool limité pour forcer l'arrêt
    engine.state.global_properties["quarantine_zone"] = [e3.id]  # La membrane est en quarantaine, impossible de s'y lier
    
    # Lancement de l'expérimentation (Boucle Dynamique - Déterministe)
    exp = Experiment(engine, constraint_providers=[oo_provider])
    exp.run_cycles(15, mode=ExplorationMode.DETERMINISTIC)

if __name__ == "__main__":
    test_meo_v03()
