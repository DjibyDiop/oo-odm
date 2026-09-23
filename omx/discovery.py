from typing import List, Dict, Any

class DiscoveryEngine:
    """
    O-DISCOVERY: Moteur de Découverte (Le plus futuriste)
    Son rôle: Utiliser l'historique, les échecs et les émergences pour décider
    quelle expérience mérite d'être tentée ensuite.
    C'est ici qu'un modèle cognitif (IA) pourrait être injecté.
    """
    def __init__(self):
        self.history = []
        
    def propose_next_experiment(self, characterization_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse le rapport de caractérisation pour synthétiser une Découverte (DISCOVERY).
        Au lieu d'une simple chaîne, retourne un objet structuré avec les statistiques de reproductibilité.
        """
        self.history.append(characterization_report)
        
        emergences = characterization_report.get("emergences", [])
        
        if not emergences:
            return {
                "type": "DISCOVERY",
                "status": "NO_EMERGENCE",
                "message": "Aucune différence structurelle ou capacité nouvelle n'a émergé de cette trajectoire.",
                "emergences_reproductibles": []
            }
            
        # MT01: Statistiques basiques d'émergence
        # On regroupe par type d'émergence
        freq = {}
        for e in emergences:
            t = e["type"]
            freq[t] = freq.get(t, 0) + 1
            
        total_trajectories = characterization_report.get("terminal_trajectories_count", 1)
        
        reproducible = []
        for t, count in freq.items():
            confidence = count / total_trajectories
            if "_INSTABLE" in t:
                confidence = 0.3  # Simulation of low reproducibility
            
            reproducible.append({
                "type": t,
                "confidence": confidence,
                "is_high_confidence": confidence >= 0.5
            })
            
        return {
            "type": "DISCOVERY",
            "status": "EMERGENCE_FOUND",
            "message": f"Découverte (O-DISCOVERY): Des futurs structurels distincts ont émergé.",
            "emergences_reproductibles": reproducible
        }
