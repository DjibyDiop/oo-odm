from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.meo_engine import Espace
from meo.transformations import Transformation
from meo.constraints import ConstraintProvider

from omx.dynamics import DynamicsEngine
from omx.exploration import ExplorationEngine
from omx.characterization import CharacterizationEngine
from omx.discovery import DiscoveryEngine

from omx.oir import OIRInstruction, OIRType
from omx.o_core import OCoreEngine
from omx.o_rust import ORustEngine
from omx.o_cpp import OCppEngine
from omx.o_py import OPyEngine
from omx.o_dplus import ODPlusEngine

class OMXOrchestrator:
    """
    OMX (Organic Multipurpose Engine) - L'Orchestrateur
    Coordonne O-DYNAMICS, O-EXPLORATION, O-CHARACTERIZATION, et O-DISCOVERY,
    tout en distribuant les tâches aux sous-moteurs spécialisés (Rust, C++, Python, D+) via OIR.
    """
    def __init__(self, constraint_providers: List[ConstraintProvider] = None):
        print("[OMX] Initialisation de l'Orchestrateur...")
        self.dynamics = DynamicsEngine()
        self.exploration = ExplorationEngine(self.dynamics, constraint_providers)
        self.characterization = CharacterizationEngine()
        self.discovery = DiscoveryEngine()
        
        # Initialisation des environnements d'exécution OMX
        self.o_rust = ORustEngine()
        self.o_cpp = OCppEngine()
        self.o_py = OPyEngine()
        self.o_dplus = ODPlusEngine()
        
    def register_transformation(self, trans: Transformation):
        self.dynamics.register_transformation(trans)
        
    def add_constraint(self, provider: ConstraintProvider):
        self.exploration.constraint_providers.append(provider)
        
    def run_experiment_cycle(self, initial_espace: Espace, max_depth: int = 2):
        print(f"\n[OMX] Lancement d'une expérience (Profondeur: {max_depth})")
        
        # Core Memory Init
        o_core = OCoreEngine(initial_espace)
        
        # 0. D+ / Rust Checks
        # Formulation de l'intention pour la Constitution
        intent_payload = {
            "intention": "EXPLORE_SCENARIO",
            "execution_scope": "SANDBOX",
            "real_state_write": False,
            "espace": initial_espace
        }
        dplus_result = self.o_dplus.process(OIRInstruction(OIRType.EVALUATE_RULES, intent_payload))
        if dplus_result.get("verdict") != "ALLOW":
            print(f"         [OMX] 🛑 OPÉRATION REJETÉE PAR LA CONSTITUTION : {dplus_result.get('verdict')}")
            return {"status": "REJECTED_BY_CONSTITUTION", "verdict": dplus_result.get("verdict")}
            
        self.o_rust.process(OIRInstruction(OIRType.ANALYZE_MEMORY, {"espace": initial_espace}))
        
        # 1. EXPLORATION (qui utilise DYNAMICS en interne)
        print("      -> O-EXPLORATION : Génération de l'arbre des possibles...")
        self.o_cpp.process(OIRInstruction(OIRType.COMPUTE_DYNAMICS, {})) # Délégation simulée au C++
        root_node, stats = self.exploration.build_possibility_tree(o_core.get_readonly_state(), max_depth)
        leaves = self.exploration.extract_leaves(root_node)
        
        print("\n         [O-EXPLORATION STATS]")
        print(f"           - Nœuds générés : {stats['nodes_generated']}")
        print(f"           - Nœuds développés : {stats['nodes_expanded']}")
        print(f"           - Nœuds rejetés (Non admissibles) : {stats['nodes_rejected']}")
        for reason, count in stats['pruning_reasons'].items():
            print(f"             * {reason} : {count}")
        print(f"           - Facteur de branchement max : {stats['max_branching_factor']}")
        print(f"           - Trajectoires terminales valides : {stats['terminal_trajectories']}")
        
        # 2. CHARACTERIZATION (Émergence)
        print("      -> O-CHARACTERIZATION : Analyse comparative des trajectoires...")
        self.o_py.process(OIRInstruction(OIRType.ANALYZE_PATTERNS, {})) # Délégation simulée à Python/IA
        report = self.characterization.analyze_trajectories(leaves, initial_espace)
        report["terminal_trajectories_count"] = stats["terminal_trajectories"]
        
        emergences = report.get("emergences", [])
        if emergences:
            print("         [*] DÉCOUVERTE ! Des anomalies structurelles ont été identifiées.")
        else:
            print("         [ ] Aucune anomalie détectée.")
            
        # 3. DISCOVERY
        print("      -> O-DISCOVERY : Synthèse et recommandation...")
        discovery_payload = self.discovery.propose_next_experiment(report)
        print(f"         {discovery_payload.get('message', '')}")
        
        report["discovery"] = discovery_payload
        report["stats"] = stats
        return report
