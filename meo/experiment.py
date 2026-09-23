import random
from enum import auto, Enum
from typing import List, Dict, Any
from .meo_engine import OrganicExplorationEngine, Espace, Bloc
from .constraints import ConstraintProvider

class ExplorationMode(Enum):
    RANDOM = auto()
    DETERMINISTIC = auto()
    EXHAUSTIVE = auto()

class TrajectoryNode:
    def __init__(self, espace: Espace, transformation: str = None, args: Dict[str, Any] = None, parent=None, depth: int = 0):
        self.espace = espace
        self.transformation = transformation
        self.args = args
        self.parent = parent
        self.depth = depth
        self.children: List['TrajectoryNode'] = []
        
    def add_child(self, child_node: 'TrajectoryNode'):
        self.children.append(child_node)
        
    @property
    def path(self) -> List[Dict[str, Any]]:
        if self.parent is None:
            return []
        p = self.parent.path
        p.append({"operation": self.transformation, "args": self.args})
        return p

class Experiment:
    def __init__(self, engine: OrganicExplorationEngine, constraint_providers: List[ConstraintProvider] = None, max_depth: int = 1, mode: ExplorationMode = ExplorationMode.DETERMINISTIC):
        self.engine = engine
        self.constraint_providers = constraint_providers or []
        self.max_depth = max_depth
        self.mode = mode
        self.trajectories_leaves: List[TrajectoryNode] = []
        self.root: TrajectoryNode = None

    def run(self):
        if self.mode == ExplorationMode.EXHAUSTIVE:
            self.root = self.explore_exhaustive(self.max_depth)
            self.trajectories_leaves = self._collect_leaves(self.root)
            return self.trajectories_leaves
        else:
            return self.run_cycles(self.max_depth, mode=self.mode)

    def _collect_leaves(self, root: TrajectoryNode) -> List[TrajectoryNode]:
        leaves = []
        def dfs(node: TrajectoryNode):
            if not node.children:
                leaves.append(node)
            else:
                for child in node.children:
                    dfs(child)
        dfs(root)
        return leaves
        
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

    def print_espace(self, cycle: int):
        self._print_espace_obj(self.engine.espace, f"\nEspace E{cycle}")

    def _print_espace_obj(self, espace: Espace, prefix: str):
        print(prefix)
        print(f"  Blocs: {', '.join([b.name for b in espace.blocs.values()])} (ATP={espace.global_properties.get('atp_pool', 0)})")
        
        relations_str = []
        for r in espace.relations:
            src = espace.blocs[r.source_id].name if r.source_id in espace.blocs else r.source_id
            tgt = espace.blocs[r.target_id].name if r.target_id in espace.blocs else r.target_id
            relations_str.append(f"{src}-{tgt}")
        
        rel_display = " ".join(relations_str) if relations_str else "aucune"
        if relations_str:
            print(f"  Relations: {rel_display}")

    def explore_exhaustive(self, max_depth: int) -> TrajectoryNode:
        """
        Explore de manière exhaustive l'arbre des possibles jusqu'à max_depth.
        Retourne le nœud racine de l'arbre généré.
        """
        root = TrajectoryNode(espace=self.engine.espace.clone(), depth=0)
        queue = [root]
        
        while queue:
            current_node = queue.pop(0)
            
            if current_node.depth >= max_depth:
                continue
                
            original_espace = self.engine.espace
            self.engine.espace = current_node.espace
            
            raw_possibilities = self.engine.get_possibilities()
            valid_possibilities, _ = self.filter_possibilities(current_node.espace, raw_possibilities)
            
            self.engine.espace = original_espace
            
            for p in valid_possibilities:
                next_espace = current_node.espace.clone()
                trans_obj = next(t for t in self.engine.transformations if t.name == p["operation"])
                next_espace = trans_obj.execute(next_espace, **p["args"])
                if "atp_pool" in next_espace.global_properties:
                    next_espace.global_properties["atp_pool"] -= p["atp_cost"]
                
                child_node = TrajectoryNode(
                    espace=next_espace,
                    transformation=p["operation"],
                    args=p["args"],
                    parent=current_node,
                    depth=current_node.depth + 1
                )
                current_node.add_child(child_node)
                queue.append(child_node)
                
        return root

    def run_cycles(self, num_cycles: int, mode: ExplorationMode = ExplorationMode.DETERMINISTIC):
        print("[ODM] Laboratoire des Possibilités")
        
        if mode == ExplorationMode.DETERMINISTIC:
            random.seed(42)
            
        for cycle in range(num_cycles):
            self.print_espace(cycle)
            
            raw_possibilities = self.engine.get_possibilities()
            valid_possibilities, invalid_possibilities = self.filter_possibilities(self.engine.espace, raw_possibilities)
            
            if not valid_possibilities:
                break
                
            if mode in (ExplorationMode.DETERMINISTIC, ExplorationMode.RANDOM):
                chosen_trans_data = random.choice(valid_possibilities)
            else:
                chosen_trans_data = valid_possibilities[0]
                
            trans_name = chosen_trans_data["operation"]
            args = chosen_trans_data["args"]
            cost = chosen_trans_data["atp_cost"]
            args_str = ", ".join([self.engine.espace.blocs[v].name if ("id" in k and v in self.engine.espace.blocs) else str(v) for k, v in args.items()])
            
            print("\n[ODM]")
            print("Transformation :")
            print(f"  {trans_name}({args_str})")
            
            trans_obj = next(t for t in self.engine.transformations if t.name == trans_name)
            self.engine.espace = trans_obj.execute(self.engine.espace, **args)
            if "atp_pool" in self.engine.espace.global_properties:
                self.engine.espace.global_properties["atp_pool"] -= cost
            
            # Print potentially new blocs
            if trans_name == "COMPOSITION":
                # Very naive way to display newly created blocs for tracing
                print("\n[ODM]")
                print("Création :")
                # Assuming the last bloc added is the new one
                new_bloc = list(self.engine.espace.blocs.values())[-1]
                print(f"  {new_bloc.name}")
            
            self.engine.history.append({"cycle": cycle, "transformation": trans_name, "args": args})

        if valid_possibilities:
            self.print_espace(num_cycles)
            print("\nCYCLE LIMIT REACHED")
            print("ESPACE VALID")
            print("CONSTRAINTS VALID")
            print("NO INVALID TRANSFORMATION")
            if mode == ExplorationMode.DETERMINISTIC:
                print("TRAJECTORY REPRODUCIBLE")
