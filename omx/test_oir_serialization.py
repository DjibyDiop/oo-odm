import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.ontology import Bloc, Liaison, Structure
from meo.meo_engine import Espace
from omx.oir import OIRInstruction, OIRType, OIRSerializer
import json

def test_oir_lossless_serialization():
    print("=== TEST OIR : SÉRIALISATION LOSSLESS (JSON) ===")
    
    # 1. Création d'un Espace complexe
    espace_original = Espace()
    
    # Blocs libres
    b1 = Bloc("B1", forme="○", caracteristiques={"nature": "fluide", "energy": 42})
    b2 = Bloc("B2", forme="□", caracteristiques={"catalyst": True})
    espace_original.add_bloc_libre(b1)
    espace_original.add_bloc_libre(b2)
    
    # Structure complexe
    b3 = Bloc("B3", forme="△")
    b4 = Bloc("B4", forme="△")
    l1 = Liaison(b3.id, b4.id, nature="forte")
    
    struct = Structure("S_Triangles")
    struct.add_bloc(b3)
    struct.add_bloc(b4)
    struct.add_liaison(l1)
    
    espace_original.add_structure(struct)
    espace_original.global_properties["atp_pool"] = 1337
    
    # Signature originelle
    # Pour calculer une signature brute, on s'assure qu'elle est comparable
    def compute_signature(e: Espace) -> str:
        b_sigs = sorted([b.signature() for b in e.blocs_libres.values()])
        s_sigs = sorted([s.topologie() for s in e.structures])
        return f"BLOCS:{'|'.join(b_sigs)} - STRUCTS:{'|'.join(s_sigs)} - ATP:{e.global_properties.get('atp_pool')}"

    sig_originale = compute_signature(espace_original)
    print(f"[1] Signature Espace Original : {sig_originale}")
    
    # 2. Création de l'instruction OIR
    print("\n[2] Encodage en OIRInstruction (JSON)...")
    instruction = OIRInstruction(OIRType.COMPUTE_DYNAMICS, {"espace": espace_original}, parameters={"max_depth": 3}, origin="O-D+")
    json_payload = instruction.to_json()
    
    print(f"--- PAYLOAD JSON GÉNÉRÉ ---")
    print(json_payload[:300] + "\n... (tronqué) ...\n" + json_payload[-100:])
    
    # 3. Décodage depuis le JSON
    print("\n[3] Décodage depuis le JSON (Simulation de réception depuis C++/Rust)...")
    reconstructed_instruction = OIRInstruction.from_json(json_payload)
    espace_reconstruit = reconstructed_instruction.payload["espace"]
    
    sig_reconstruite = compute_signature(espace_reconstruit)
    print(f"Signature Espace Reconstruit : {sig_reconstruite}")
    
    # 4. Vérification Lossless Stricte
    success = True
    print("\n[4] Vérification de l'intégrité (Champs par champs)...")
    
    # Vérification des blocs libres
    for b_id, b in espace_original.blocs_libres.items():
        if b_id not in espace_reconstruit.blocs_libres:
            print(f"❌ ERREUR : Bloc {b_id} manquant.")
            success = False
            continue
        br = espace_reconstruit.blocs_libres[b_id]
        if b.forme != br.forme or b.name != br.name or b.caracteristiques != br.caracteristiques:
            print(f"❌ ERREUR : Altération du Bloc {b.name}.")
            success = False
            
    # Vérification des structures
    for i, s in enumerate(espace_original.structures):
        sr = espace_reconstruit.structures[i]
        if s.id != sr.id or s.name != sr.name or len(s.blocs) != len(sr.blocs) or len(s.liaisons) != len(sr.liaisons):
            print(f"❌ ERREUR : Altération de la Structure {s.name}.")
            success = False
            
    # Vérification des propriétés globales
    if espace_original.global_properties != espace_reconstruit.global_properties:
        print("❌ ERREUR : Altération des global_properties.")
        success = False

    # Validation finale par signature
    if sig_originale == sig_reconstruite and success:
        print("\n✅ SUCCÈS TOTAL : La sérialisation est strictement Lossless. E₀ ≡ E₁")
        print(f"    Message ID : {reconstructed_instruction.message_id}")
        print(f"    Paramètres : {reconstructed_instruction.parameters}")
    else:
        print("\n❌ ÉCHEC DE LA SÉRIALISATION.")
        print(f"Attendu : {sig_originale}")
        print(f"Obtenu  : {sig_reconstruite}")

if __name__ == "__main__":
    test_oir_lossless_serialization()
