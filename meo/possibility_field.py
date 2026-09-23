"""
OO-ODM — Organisme de Possibilités (Possibility Field)
Défini dans plan.md (L14550-14605) :
Maintient une cartographie dynamique de :
  - Ce qui existe (E)
  - Ce qui est possible (P)
  - Ce qui a déjà été essayé (H)
  - Ce qui a émergé (★)
  - Ce qui est interdit / impossible (I)
  - Ce qui reste inexploré (U)
"""
from typing import Dict, List, Any, Set, Optional
import hashlib
import json
from .meo_engine import Espace
from .ontology import EmergenceReport

def hash_espace(espace: Espace) -> str:
    """Produit une signature canonique et déterministe d'un Espace."""
    blocs_sig = sorted([b.signature() for b in espace.blocs.values()])
    structs_sig = sorted([s.topologie() for s in espace.structures])
    raw = f"B:{','.join(blocs_sig)}|S:{','.join(structs_sig)}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]

class PossibilityField:
    """
    Champ Dynamique des Possibilités OdM.
    Laboratoire d'exploration épistémique pour le macro-organisme OO.
    """
    def __init__(self, initial_espace: Optional[Espace] = None):
        self.generation = 0
        self.states: Dict[str, Espace] = {}
        self.history_trajectories: List[List[str]] = []
        self.emergences: List[Dict[str, Any]] = []
        self.forbidden_transitions: List[Dict[str, Any]] = []
        self.unexplored_frontier: Set[str] = set()
        
        if initial_espace:
            h = hash_espace(initial_espace)
            self.states[h] = initial_espace.clone()
            self.unexplored_frontier.add(h)
            
    def record_step(self, before_espace: Espace, op_name: str, args: Dict[str, Any], after_espace: Espace) -> str:
        """Enregistre une transition d'état P_t -> P_{t+1}."""
        self.generation += 1
        h_before = hash_espace(before_espace)
        h_after = hash_espace(after_espace)
        
        self.states[h_before] = before_espace.clone()
        self.states[h_after] = after_espace.clone()
        
        if h_before in self.unexplored_frontier:
            self.unexplored_frontier.remove(h_before)
            
        self.unexplored_frontier.add(h_after)
        
        traj_entry = f"{h_before} --[{op_name}]--> {h_after}"
        if not self.history_trajectories or len(self.history_trajectories[-1]) >= 10:
            self.history_trajectories.append([traj_entry])
        else:
            self.history_trajectories[-1].append(traj_entry)
            
        return h_after

    def record_emergence(self, report: EmergenceReport, state_hash: str):
        """Enregistre une émergence ★ identifiée dans le champ."""
        self.emergences.append({
            "generation": self.generation,
            "state_hash": state_hash,
            "report": report.to_dict()
        })

    def record_impossibility(self, state_hash: str, operation: str, reason: str):
        """Mémorise ce qui est impossible ou interdit (Lois physiques / Constitution)."""
        self.forbidden_transitions.append({
            "generation": self.generation,
            "state_hash": state_hash,
            "operation": operation,
            "reason": reason
        })

    def coverage_metrics(self) -> Dict[str, Any]:
        """Mesure l'étendue du territoire de possibilités exploré."""
        total_discovered = len(self.states)
        total_frontier = len(self.unexplored_frontier)
        total_emergences = len(self.emergences)
        total_forbidden = len(self.forbidden_transitions)
        
        return {
            "generation": self.generation,
            "known_states_count": total_discovered,
            "frontier_unexplored_count": total_frontier,
            "emergence_count": total_emergences,
            "forbidden_count": total_forbidden,
            "ratio_novelty": (total_emergences / max(1, total_discovered)) * 100.0
        }

    def summary(self) -> str:
        m = self.coverage_metrics()
        return (
            f"=== CHAMP DES POSSIBILITÉS OdM (Gen {m['generation']}) ===\n"
            f"  États connus (E)       : {m['known_states_count']}\n"
            f"  Frontière inexplorée (U): {m['frontier_unexplored_count']}\n"
            f"  Émergences singulières (★): {m['emergence_count']}\n"
            f"  Transitions interdites (I): {m['forbidden_count']}\n"
            f"  Indice de nouveauté    : {m['ratio_novelty']:.1f}%"
        )
