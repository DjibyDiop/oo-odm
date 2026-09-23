from typing import List, Dict, Any, Tuple
from .meo_engine import Espace
from .experiment import TrajectoryNode
from .ontology import EmergenceReport, EmergenceType

class Comparer:
    """
    O-CHARACTERIZATION (Interne): Observe les états terminaux et génère
    les EmergenceReports structurés.
    """
    def __init__(self):
        pass
        
    def _compute_espace_signature(self, espace: Espace) -> str:
        """
        Calcule une empreinte de l'Espace basée sur ses structures et blocs libres.
        """
        b_sigs = sorted([b.signature() for b in espace.blocs_libres.values()])
        s_sigs = sorted([s.topologie() for s in espace.structures])
        return f"BLOCS:{'|'.join(b_sigs)} - STRUCTS:{'|'.join(s_sigs)}"

    def compare_nodes(self, leaves: List[TrajectoryNode]) -> Dict[str, Any]:
        report = {
            "trajectories": [],
            "emergences": []
        }
        
        # On va chercher les anomalies (ex: nouvelle structure, nouvelle capacité)
        for i, leaf in enumerate(leaves):
            path_str = " -> ".join([step["operation"] for step in leaf.path])
            espace = leaf.espace
            
            sig = self._compute_espace_signature(espace)
            
            report["trajectories"].append({
                "id": f"T{i}",
                "path": path_str,
                "signature": sig
            })
            
            # Détection d'émergence structurelle:
            # Si on a créé une structure "active" ou un bloc composé ("□")
            for struct in espace.structures:
                if "active" in struct.capacites_structurelles():
                    em = EmergenceReport(
                        type=EmergenceType.NOUVELLE_CAPACITE,
                        description=f"La structure {struct.name} a déverrouillé une capacité active.",
                        source_path=f"T{i}"
                    )
                    report["emergences"].append(em.to_dict())
            
            for bloc in espace.blocs_libres.values():
                if bloc.forme == "□" and "composed_from" in bloc.caracteristiques:
                    em = EmergenceReport(
                        type=EmergenceType.NOUVELLE_STRUCTURE,
                        description=f"Le bloc composé {bloc.name} a été formé.",
                        source_path=f"T{i}"
                    )
                    report["emergences"].append(em.to_dict())

        return report
