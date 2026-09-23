from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.meo_engine import Espace
from meo.constraints import ConstraintProvider
from meo.experiment import TrajectoryNode
from omx.dynamics import DynamicsEngine

class ExplorationEngine:
    """
    O-EXPLORATION: Moteur d'Exploration
    Son rôle: Chercher ce qui pourrait arriver en naviguant dans l'arbre des possibles.
    Il utilise le DynamicsEngine pour avancer.
    """
    def __init__(self, dynamics_engine: DynamicsEngine, constraint_providers: List[ConstraintProvider] = None):
        self.dynamics = dynamics_engine
        self.constraint_providers = constraint_providers or []
        
    def filter_possibilities(self, espace: Espace, possibilities: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[tuple[Dict[str, Any], str]]]:
        valid = []
        invalid = []
        for p in possibilities:
            is_valid = True
            reject_reason = ""
            for provider in self.constraint_providers:
                ok, reason = provider.evaluate(espace, p)
                if not ok:
                    is_valid = False
                    reject_reason = reason
                    break
            
            if is_valid:
                valid.append(p)
            else:
                invalid.append((p, reject_reason))
        return valid, invalid

    def build_possibility_tree(self, initial_espace: Espace, max_depth: int) -> tuple[TrajectoryNode, Dict[str, Any]]:
        """
        Génère l'arbre des trajectoires possibles (BFS).
        Retourne le nœud racine et les statistiques d'exploration.
        """
        stats = {
            "nodes_generated": 1,
            "nodes_rejected": 0,
            "nodes_expanded": 0,
            "terminal_trajectories": 0,
            "max_depth": max_depth,
            "max_branching_factor": 0,
            "pruning_reasons": {}
        }
        root = TrajectoryNode(espace=initial_espace.clone(), depth=0)
        queue = [root]
        
        while queue:
            current_node = queue.pop(0)
            
            if current_node.depth >= max_depth:
                continue
                
            stats["nodes_expanded"] += 1
                
            raw_possibilities = self.dynamics.get_raw_possibilities(current_node.espace)
            valid_possibilities, invalid_possibilities = self.filter_possibilities(current_node.espace, raw_possibilities)
            
            stats["nodes_rejected"] += len(invalid_possibilities)
            for _, reason in invalid_possibilities:
                stats["pruning_reasons"][reason] = stats["pruning_reasons"].get(reason, 0) + 1
                
            if len(valid_possibilities) > stats["max_branching_factor"]:
                stats["max_branching_factor"] = len(valid_possibilities)
            
            for p in valid_possibilities:
                # O-DYNAMICS simule l'état futur
                next_espace = self.dynamics.apply_transformation(current_node.espace, p)
                
                child_node = TrajectoryNode(
                    espace=next_espace,
                    transformation=p["operation"],
                    args=p["args"],
                    parent=current_node,
                    depth=current_node.depth + 1
                )
                current_node.add_child(child_node)
                queue.append(child_node)
                stats["nodes_generated"] += 1
                
        # Calculer le nombre de trajectoires terminales
        leaves = self.extract_leaves(root)
        stats["terminal_trajectories"] = len(leaves)
                
        return root, stats

    def extract_leaves(self, node: TrajectoryNode) -> List[TrajectoryNode]:
        """
        Extrait toutes les trajectoires terminales de l'arbre.
        """
        if not node.children:
            return [node]
        leaves = []
        for child in node.children:
            leaves.extend(self.extract_leaves(child))
        return leaves
