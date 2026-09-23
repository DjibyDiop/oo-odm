import subprocess
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_case(name: str, payload: str, expected_type: str, expected_reason: str = None):
    print(f"[{name}] Envoi du message...")
    
    exe_name = "oir-rust.exe" if os.name == "nt" else "oir-rust"
    binary_path = os.path.join(os.path.dirname(__file__), "oir-rust", "target", "release", exe_name)
    if not os.path.exists(binary_path):
        alt_name = "oir-rust" if exe_name == "oir-rust.exe" else "oir-rust.exe"
        alt_path = os.path.join(os.path.dirname(__file__), "oir-rust", "target", "release", alt_name)
        if os.path.exists(alt_path):
            binary_path = alt_path
            
    process = subprocess.Popen(
        [binary_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=payload + "\n", timeout=2)
    
    if not stdout.strip():
        print(f"  ❌ ÉCHEC : Aucune réponse. Stderr: {stderr.strip()}")
        return False
        
    try:
        response = json.loads(stdout.strip())
        msg_type = response.get("message_type")
        
        if msg_type != expected_type:
            print(f"  ❌ ÉCHEC : Type attendu '{expected_type}', obtenu '{msg_type}'.")
            return False
            
        if expected_type == "error":
            reason = response.get("error", {}).get("reason", "")
            if expected_reason and expected_reason not in reason:
                print(f"  ❌ ÉCHEC : Raison attendue '{expected_reason}', obtenue '{reason}'.")
                return False
            print(f"  ✅ PASS (Rejeté avec succès : {reason})")
        else:
            print(f"  ✅ PASS (Résultat valide reçu)")
            
        return True
    except json.JSONDecodeError:
        print(f"  ❌ ÉCHEC : Réponse non-JSON. Obtenu : {stdout.strip()}")
        return False

def run_all_tests():
    print("=== TEST OIR IPC & CORRUPTION ===")
    
    valid_payload = json.dumps({
        "oir_version": "1.0",
        "message_type": "instruction",
        "metadata": {"origin": "TEST", "message_id": "123"},
        "instruction": {"operation": "ANALYZE_MEMORY"},
        "payload": {"espace": {"blocs_libres": [{}], "structures": []}}
    })
    
    unknown_version = json.dumps({
        "oir_version": "2.0",
        "message_type": "instruction",
        "metadata": {"origin": "TEST"},
        "instruction": {"operation": "ANALYZE_MEMORY"},
        "payload": {}
    })
    
    missing_payload = json.dumps({
        "oir_version": "1.0",
        "message_type": "instruction",
        "metadata": {"origin": "TEST"},
        "instruction": {"operation": "ANALYZE_MEMORY"}
    })
    
    unknown_operation = json.dumps({
        "oir_version": "1.0",
        "message_type": "instruction",
        "metadata": {"origin": "TEST"},
        "instruction": {"operation": "DO_SOMETHING_MAGIC"},
        "payload": {}
    })
    
    malformed_json = '{"oir_version": "1.0", "message_type": '
    
    results = [
        test_case("OIR Valide", valid_payload, "result"),
        test_case("Version Inconnue", unknown_version, "error", "UNKNOWN version"),
        test_case("JSON Malformé", malformed_json, "error", "malformed JSON"),
        test_case("Payload Manquant", missing_payload, "error", "missing payload"),
        test_case("Opération Inconnue", unknown_operation, "error", "UNKNOWN type"),
    ]
    
    if all(results):
        print("\n✅ TOUS LES TESTS IPC ONT RÉUSSI. La membrane OIR est étanche.")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ.")

if __name__ == "__main__":
    run_all_tests()
