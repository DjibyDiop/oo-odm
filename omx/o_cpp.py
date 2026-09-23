import os
import subprocess
import json
from typing import Any
from .oir import OIRInstruction, OIRType

class OCppEngine:
    """
    O-CPP: Moteur de Calcul Haute Performance (HPC / SIMD Topologique)
    Exécute le binaire compilé natif ocpp_engine.exe pour accélérer
    le calcul et l'élagage combinatoire de l'arbre des possibles.
    RÈGLE ABSOLUE : ZÉRO MOCKS.
    """
    def __init__(self):
        self.bin_path = os.path.join(os.path.dirname(__file__), "cpp_engine", "ocpp_engine.exe")
        if not os.path.exists(self.bin_path):
            raise FileNotFoundError(f"[O-CPP FATAL] Binaire natif introuvable : {self.bin_path}")
        print("[O-CPP] Moteur SIMD HPC chargé (Binaire natif C++).")
        
    def process(self, instruction: OIRInstruction) -> Any:
        if instruction.op_type == OIRType.COMPUTE_DYNAMICS:
            print("         [O-CPP] Accélération du calcul de l'arbre des possibles (SIMD Natif C++)...")
            
            payload = instruction.payload or {}
            depth = payload.get("depth", 3)
            blocs_count = payload.get("blocs_count", 5)
            relaxed = payload.get("relaxed", False)
            
            cmd = [self.bin_path, "--depth", str(depth), "--blocs", str(blocs_count)]
            if relaxed:
                cmd.append("--relaxed")
                
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
                res = json.loads(proc.stdout.strip())
                return res
            except Exception as e:
                return {
                    "status": "ERROR",
                    "engine": "O-CPP-NATIVE-HPC",
                    "error": str(e)
                }
                
        return {"status": "ignored"}
