"""
OdM — OMX Bridge (Phase 3 & 4)
Pont entre odm_core_v02 (Expériences & Organisme de Possibilités) et les moteurs natifs OMX.

Rôles :
  1. Arbitrage Constitutionnel D+ (O-D+, dplus/odm_sandbox.plus)
  2. Validation Ontologique D+ (O-D+, dplus/odm_ontology.plus)
  3. Suivi du Champ des Possibilités D+ (O-D+, dplus/odm_possibilities.plus)
  4. Délégation de l'expansion combinatoire à ocpp_engine.exe (O-CPP)
  5. Calculs d'entropie informationnelle et invariants topologiques (O-PY)
  6. Enveloppe stricte OIR v1.0 inter-moteurs

Zero Mocks : tout appel passe par les binaires et chaînes natives (dpc.exe, ocpp_engine.exe).
"""

import sys
import os
import json
from typing import Any, Dict, List

# Chemin racine pour importer omx/
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from omx.oir import OIRInstruction, OIRType
from omx.o_dplus import ODPlusEngine
from omx.o_cpp import OCppEngine
from omx.o_py import OPyEngine


# ============================================================
# VERDICT D+
# ============================================================

class ConstitutionalVerdict:
    ALLOW      = "ALLOW"
    QUARANTINE = "QUARANTINE"
    FORBID     = "FORBID"


# ============================================================
# PONT OMX ↔ OdM
# ============================================================

class OMXBridge:
    """
    Pont complet entre odm_core_v02 et les moteurs natifs OMX (D+, C++, Python).
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._dplus: ODPlusEngine = None
        self._cpp: OCppEngine = None
        self._py: OPyEngine = None
        self._init_engines()

    def _init_engines(self):
        """Initialise les moteurs natifs (Zéro Mocks)."""
        try:
            self._dplus = ODPlusEngine()
        except Exception as e:
            raise RuntimeError(f"[OMXBridge] O-D+ indisponible : {e}")

        try:
            self._cpp = OCppEngine()
        except Exception as e:
            raise RuntimeError(f"[OMXBridge] O-CPP indisponible : {e}")

        try:
            self._py = OPyEngine()
        except Exception as e:
            raise RuntimeError(f"[OMXBridge] O-PY indisponible : {e}")

    # --------------------------------------------------------
    # 1. AUTORISATION D+ (odm_sandbox.plus)
    # --------------------------------------------------------

    def authorize_cycle(
        self,
        cycle: int,
        elements: dict,
        scope: str = "SANDBOX"
    ) -> bool:
        """
        Interroge la Constitution D+ pour autoriser un cycle autonome.
        Retourne True si ALLOW, False si FORBID ou QUARANTINE.
        """
        instr = OIRInstruction(
            OIRType.EVALUATE_RULES,
            {
                "intention":        "EXPLORE_SCENARIO",
                "execution_scope":  scope,
                "real_state_write": False,
                "cycle":            cycle,
                "elements_count":   len(elements),
            }
        )

        result = self._dplus.process(instr)
        verdict = result.get("verdict", ConstitutionalVerdict.FORBID)

        if self.verbose:
            print(
                f"  [D+ GATE] cycle={cycle} → verdict={verdict} "
                f"(éléments={len(elements)}, scope={scope})"
            )

        return verdict == ConstitutionalVerdict.ALLOW

    # --------------------------------------------------------
    # 2. VALIDATION ONTOLOGIQUE D+ (odm_ontology.plus)
    # --------------------------------------------------------

    def validate_ontology(self, elements: dict) -> bool:
        """
        Valide l'intégrité biologique et les 4 formes via odm_ontology.plus.
        """
        instr = OIRInstruction(
            OIRType.VALIDATE_ONTOLOGY,
            {"elements": elements}
        )
        res = self._dplus.process(instr)
        return res.get("valid", False)

    # --------------------------------------------------------
    # 3. NOTIFICATION DU CHAMP D+ (odm_possibilities.plus)
    # --------------------------------------------------------

    def record_trajectory_dplus(
        self,
        trajectory_id: int,
        terminal_nodes: int,
        has_singularity: bool
    ) -> dict:
        """
        Enregistre la trajectoire dans l'organe de suivi D+ odm_possibilities.plus.
        """
        instr = OIRInstruction(
            OIRType.RECORD_TRAJECTORY,
            {
                "trajectory_id": trajectory_id,
                "terminal_nodes": terminal_nodes,
                "has_singularity": has_singularity,
            }
        )
        return self._dplus.process(instr)

    # --------------------------------------------------------
    # 4. EXPANSION HPC DE L'ARBRE (O-CPP)
    # --------------------------------------------------------

    def expand_tree(
        self,
        depth: int,
        element_count: int,
        relaxed: bool = False
    ) -> dict:
        """
        Délègue l'accélération combinatoire à ocpp_engine.exe.
        """
        instr = OIRInstruction(
            OIRType.COMPUTE_DYNAMICS,
            {
                "depth":       depth,
                "blocs_count": element_count,
                "relaxed":     relaxed,
            }
        )

        result = self._cpp.process(instr)

        if self.verbose:
            print(
                f"  [O-CPP HPC] depth={depth}, éléments={element_count} → "
                f"valid_trajectories={result.get('valid_trajectories', '?')}, "
                f"time={result.get('execution_time_us', '?')}µs"
            )

        return result

    # --------------------------------------------------------
    # 5. CALCUL D'ENTROPIE INFORMATIONNELLE (O-PY)
    # --------------------------------------------------------

    def compute_field_entropy(self, signatures: List[str]) -> float:
        """
        Calcule l'entropie de Shannon des signatures du champ via O-PY.
        """
        instr = OIRInstruction(
            OIRType.ANALYZE_PATTERNS,
            {"signatures": signatures}
        )
        res = self._py.process(instr)
        return res.get("shannon_entropy", 0.0)

    # --------------------------------------------------------
    # 6. RAPPORT D'ÉTAT DU PONT
    # --------------------------------------------------------

    def status(self) -> dict:
        return {
            "o_dplus_ready": self._dplus is not None,
            "o_cpp_ready":   self._cpp   is not None,
            "o_py_ready":    self._py    is not None,
        }
