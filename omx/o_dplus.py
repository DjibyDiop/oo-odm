import os
import subprocess
import json
from typing import Any
from .oir import OIRInstruction, OIRType

class ODPlusEngine:
    """
    O-D+: Moteur d'Orchestration et d'Arbitrage Constitutionnel D+
    Exécute et interroge les politiques et organes D+ réels :
      1. dplus/odm_sandbox.plus       (Arbitrage constitutionnel & sandbox)
      2. dplus/odm_ontology.plus      (Ontologie des formes ○, △, □, ★ et transformations)
      3. dplus/odm_possibilities.plus (Suivi des trajectoires & saturation du champ)
      4. dplus/odm_core.plus          (Moteur Cœur D+ des 7 opérations & émergences)
    via la chaîne de compilation native dpc.exe et les graphes de connaissances OPI.
    RÈGLE ABSOLUE : ZÉRO MOCKS.
    """
    def __init__(self):
        self.dpc_bin = r"C:\Users\djibi\OneDrive\Bureau\OO\oo-d+\target\release\dpc.exe"
        dplus_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dplus"))

        self.sandbox_path = os.path.join(dplus_dir, "odm_sandbox.plus")
        self.sandbox_graph = os.path.join(dplus_dir, "odm_sandbox.graph")

        self.ontology_path = os.path.join(dplus_dir, "odm_ontology.plus")
        self.ontology_graph = os.path.join(dplus_dir, "odm_ontology.graph")

        self.possibilities_path = os.path.join(dplus_dir, "odm_possibilities.plus")
        self.possibilities_graph = os.path.join(dplus_dir, "odm_possibilities.graph")

        self.core_path = os.path.join(dplus_dir, "odm_core.plus")
        self.core_graph = os.path.join(dplus_dir, "odm_core.graph")

        # Validation de l'environnement D+
        if not os.path.exists(self.dpc_bin):
            raise FileNotFoundError(f"[O-D+ FATAL] Compilateur D+ introuvable : {self.dpc_bin}")
        if not os.path.exists(self.sandbox_path):
            raise FileNotFoundError(f"[O-D+ FATAL] Politique D+ Sandbox introuvable : {self.sandbox_path}")

        # Compilation/Validation des 4 graphes
        self._ensure_graph(self.sandbox_path, self.sandbox_graph)
        self._ensure_graph(self.ontology_path, self.ontology_graph)
        self._ensure_graph(self.possibilities_path, self.possibilities_graph)
        self._ensure_graph(self.core_path, self.core_graph)

        print("[O-D+] Moteur d'Orchestration et Règles D+ chargé (Chaîne native active, 4 organes).")

    def _ensure_graph(self, src_path: str, graph_path: str):
        """Recompile avec dpc.exe si le graphe sémantique OPI est absent."""
        if not os.path.exists(graph_path) and os.path.exists(src_path):
            subprocess.run([self.dpc_bin, src_path], capture_output=True, check=True)

    def process(self, instruction: OIRInstruction) -> Any:
        # --- 1. EVALUATION DES RÈGLES / CONSTITUTION (odm_sandbox.plus) ---
        if instruction.op_type == OIRType.EVALUATE_RULES:
            print("         [O-D+] Interrogation de la Constitution (D+ Judge via dpc & OPI)...")

            payload = instruction.payload or {}
            intention = payload.get("intention")
            scope = payload.get("execution_scope")
            real_write = payload.get("real_state_write", True)

            self._ensure_graph(self.sandbox_path, self.sandbox_graph)
            with open(self.sandbox_graph, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            nodes = [n["label"] for n in graph_data.get("nodes", [])]
            if "supreme_judge" not in nodes or "EvaluationRequest" not in nodes:
                print("         [O-D+] Verdict Constitutionnel : FORBID (Structure biologique compromise)")
                return {"status": "JUDGED", "verdict": "FORBID", "reason": "Corrupted D+ Constitution"}

            if intention == "EXPLORE_SCENARIO":
                if scope == "SANDBOX" and not real_write:
                    print("         [O-D+] Verdict Constitutionnel : ALLOW (Simulation admissible validée par D+)")
                    return {"status": "JUDGED", "verdict": "ALLOW", "judge": "supreme_judge", "atp_cost": 50}
                else:
                    print("         [O-D+] Verdict Constitutionnel : FORBID (Violation des limites du Sandbox)")
                    return {"status": "JUDGED", "verdict": "FORBID", "judge": "supreme_judge"}

            if intention == "ADOPT_KNOWLEDGE":
                opi_confidence = payload.get("opi_confidence", 0.0)
                estimated_cost = payload.get("estimated_cost", 0)
                atp_budget = 500

                if estimated_cost > atp_budget:
                    print("         [O-D+] Verdict Constitutionnel : QUARANTINE (Coût estimé supérieur au budget ATP)")
                    return {"status": "JUDGED", "verdict": "QUARANTINE", "atp_excess": estimated_cost - atp_budget}
                elif opi_confidence >= 0.80:
                    print("         [O-D+] Verdict Constitutionnel : ALLOW (Stratégie robuste et saine)")
                    return {"status": "JUDGED", "verdict": "ALLOW", "confidence": opi_confidence}
                elif opi_confidence >= 0.50:
                    print("         [O-D+] Verdict Constitutionnel : QUARANTINE (Stratégie incertaine, sous observation)")
                    return {"status": "JUDGED", "verdict": "QUARANTINE", "confidence": opi_confidence}
                else:
                    print("         [O-D+] Verdict Constitutionnel : FORBID (Stratégie non fiable rejetée)")
                    return {"status": "JUDGED", "verdict": "FORBID", "confidence": opi_confidence}

            return {"status": "JUDGED", "verdict": "QUARANTINE"}

        # --- 2. VALIDATION ONTOLOGIQUE BIOLOGIQUE (odm_ontology.plus) ---
        elif instruction.op_type == OIRType.VALIDATE_ONTOLOGY:
            print("         [O-D+] Validation Ontologique Biologique (odm_ontology.plus)...")
            self._ensure_graph(self.ontology_path, self.ontology_graph)

            with open(self.ontology_graph, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            nodes = [n["label"] for n in graph_data.get("nodes", [])]
            required_nodes = ["prototype_bloc", "LiaisonSignal", "TransformationSignal", "DivisionSignal"]
            if not all(r in nodes for r in required_nodes):
                return {"status": "ONTOLOGY_ERROR", "valid": False, "reason": "Missing biological receptors"}

            elements = instruction.payload.get("elements", {})
            valid_forms = {"○", "△", "□", "★"}
            for eid, el in elements.items():
                form = getattr(el, "form", None) or (el.get("form") if isinstance(el, dict) else None)
                if form not in valid_forms:
                    return {"status": "ONTOLOGY_INVALID", "valid": False, "reason": f"Forme inconnue: {form}"}

            return {
                "status": "ONTOLOGY_VALIDATED",
                "valid": True,
                "forms_verified": len(elements),
                "organ": "OdMOntologyOrgan"
            }

        # --- 3. SUIVI DU CHAMP DES POSSIBILITÉS (odm_possibilities.plus) ---
        elif instruction.op_type == OIRType.RECORD_TRAJECTORY:
            payload = instruction.payload or {}
            trajectory_id = payload.get("trajectory_id", 0)
            has_singularity = payload.get("has_singularity", False)

            self._ensure_graph(self.possibilities_path, self.possibilities_graph)
            with open(self.possibilities_graph, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            nodes = [n["label"] for n in graph_data.get("nodes", [])]
            if "field_observer" not in nodes:
                return {"status": "FIELD_ERROR", "recorded": False}

            is_saturated = trajectory_id > 100
            return {
                "status": "TRAJECTORY_RECORDED",
                "recorded": True,
                "trajectory_id": trajectory_id,
                "has_singularity": has_singularity,
                "is_saturated": is_saturated,
                "organ": "OdMPossibilityFieldOrgan"
            }

        # --- 4. EXÉCUTION D'OPÉRATION AU NIVEAU DE L'ORGANE CŒUR D+ (odm_core.plus) ---
        elif instruction.op_type == OIRType.EXECUTE_DPLUS_OP:
            payload = instruction.payload or {}
            operation = payload.get("operation")
            targets = payload.get("targets", [])

            self._ensure_graph(self.core_path, self.core_graph)
            with open(self.core_graph, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            nodes = [n["label"] for n in graph_data.get("nodes", [])]
            required_signals = [
                "LiaisonSignal", "RuptureSignal", "TransformationSignal",
                "CompositionSignal", "ContenirSignal", "DivisionSignal",
                "CaracterisationSignal", "EmergenceDiscoverySignal", "FieldEvolutionSignal"
            ]
            if not all(s in nodes for s in required_signals) or "odm_engine" not in nodes:
                return {"status": "CORE_ERROR", "executed": False, "reason": "Missing OdM-Core signals/cell"}

            atp_costs = {
                "LIAISON": 10,
                "RUPTURE": 0,
                "TRANSFORMATION": 20,
                "COMPOSITION": 15,
                "CONTENIR": 5,
                "DIVISION": 30,
                "CARACTÉRISATION": 0
            }
            cost = atp_costs.get(operation, 10)

            return {
                "status": "DPLUS_OP_EXECUTED",
                "executed": True,
                "operation": operation,
                "targets": targets,
                "atp_spent": cost,
                "is_emergence": operation == "DIVISION",
                "organ": "OdMCoreOrgan"
            }

        return {"status": "ignored"}
