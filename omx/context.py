from typing import List, Dict, Any

class ExperimentContext:
    """
    ExperimentContext
    
    Représente la connaissance expérientielle de l'Organisme relative à une menace ou un domaine,
    transmise au laboratoire OdM et à OPI.
    
    Il ne modifie pas l'Espace physique, mais guide l'exploration et la délibération.
    Notamment, il contient les stratégies précédemment invalidées par le monde réel.
    """
    def __init__(self, target_threat: str):
        self.target_threat = target_threat
        self.invalidated_strategies: List[str] = []
        
    def add_invalidated_strategy(self, strategy_action: str):
        if strategy_action not in self.invalidated_strategies:
            self.invalidated_strategies.append(strategy_action)
            
    def is_invalidated(self, strategy_action: str) -> bool:
        return strategy_action in self.invalidated_strategies
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_threat": self.target_threat,
            "invalidated_strategies": self.invalidated_strategies
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentContext':
        ctx = cls(data.get("target_threat", ""))
        ctx.invalidated_strategies = data.get("invalidated_strategies", [])
        return ctx
