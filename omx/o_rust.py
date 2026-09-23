import subprocess
import json
import os
import uuid
from .oir import OIRInstruction, OIRType
from typing import Any

class ORustEngine:
    """
    O-RUST: Sécurité / Système
    Vérifie l'intégrité de la mémoire, les pointeurs, et les contraintes
    constitutionnelles critiques sans garbage collection overhead.
    """
    def __init__(self):
        exe_name = "oir-rust.exe" if os.name == "nt" else "oir-rust"
        p = os.path.join(os.path.dirname(__file__), "oir-rust", "target", "release", exe_name)
        if not os.path.exists(p):
            # Fallback check for either variant
            alt_name = "oir-rust" if exe_name == "oir-rust.exe" else "oir-rust.exe"
            alt_p = os.path.join(os.path.dirname(__file__), "oir-rust", "target", "release", alt_name)
            if os.path.exists(alt_p):
                p = alt_p
        self.engine_path = p
        
    def process(self, instruction: OIRInstruction) -> Any:
        if instruction.op_type == OIRType.ANALYZE_MEMORY:
            # Sérialiser l'instruction dans une enveloppe OIR v1.0
            # (Le message_id et origin sont gérés par OIRInstruction ou seront ignorés car on veut juste la trame)
            json_payload = instruction.to_json()
            
            # Appel IPC via stdin/stdout
            try:
                print("         [O-RUST IPC] Analyse de la sécurité de l'Espace en cours (IPC vers Rust Natif)...")
                process = subprocess.Popen(
                    [self.engine_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                
                # Envoi et réception
                stdout, stderr = process.communicate(input=json_payload + "\n", timeout=5)
                
                if process.returncode != 0 or not stdout.strip():
                    print(f"         [O-RUST IPC ERROR] Le processus externe a échoué. Stderr: {stderr}")
                    return {"status": "error"}
                    
                # Parsing de la réponse OIR (RESULT)
                response = json.loads(stdout.strip())
                
                if response.get("message_type") == "result":
                    payload = response.get("payload", {})
                    status = payload.get("status", "UNKNOWN")
                    msg = payload.get("message", "")
                    print(f"         [O-RUST IPC] Protocole Validé : {status} ({msg})")
                    return response
                else:
                    print("         [O-RUST IPC ERROR] Réponse inattendue.")
                    return {"status": "error"}
                    
            except Exception as e:
                print(f"         [O-RUST IPC ERROR] {e}")
                return {"status": "error"}
                
        return {"status": "ignored"}
