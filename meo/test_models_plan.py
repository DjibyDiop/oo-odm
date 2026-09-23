import sys
import os

# Ensure UTF-8 output on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meo.model_001_absorption import Model001Absorption
from meo.model_002_epreuve_vide import Model002EpreuveDuVide
from meo.model_003_cire_qui_fond import Model003CireQuiFond
from meo.possibility_field import PossibilityField
from meo.meo_engine import Espace
from meo.ontology import Bloc, FORM_CIRCLE, FORM_STAR

def test_models_plan():
    print("=== TEST DES 3 MODÉLISATIONS CANONIQUES DE PLAN.MD ===")
    
    # 1. Modélisation 001 : Absorption
    print("\n--- [MODÈLE 001] L'Absorption ---")
    m1 = Model001Absorption(initial_energy_a=100)
    res1 = m1.run_full()
    print(f"  Énergie finale Source A    : {res1['step2']['energy_a']}")
    print(f"  Énergie finale Récepteur B : {res1['step2']['energy_b']}")
    print(f"  Activation / Émergence     : {res1['step2']['emergence']}")
    assert res1['step2']['energy_b'] == 70
    assert res1['step2']['emergence'] == True
    print("  --> [OK] Modèle 001 Validé.")
    
    # 2. Modélisation 002 : Épreuve du Vide
    print("\n--- [MODÈLE 002] L'Épreuve du Vide (5 Épreuves) ---")
    m2 = Model002EpreuveDuVide()
    res2 = m2.run_all_epreuves()
    for name, ok in res2.items():
        print(f"  Épreuve {name}: {'PASS' if ok else 'FAIL'}")
        assert ok, f"Échec de l'épreuve {name}"
    print("  --> [OK] Modèle 002 Validé.")
    
    # 3. Modélisation 003 : La Cire qui fond
    print("\n--- [MODÈLE 003] La Cire qui fond (Transition de Phase) ---")
    m3 = Model003CireQuiFond(initial_temp=20.0, seuil_fusion=60.0)
    history = m3.run_simulation()
    print(f"  Phase initiale (45°C)  : {history[0]['phase']} (Formes: {history[0]['formes']})")
    print(f"  Phase après fusion (70°C): {history[1]['phase']} (Formes: {history[1]['formes']})")
    assert history[0]['phase'] == "SOLIDE"
    assert history[1]['phase'] == "LIQUIDE"
    assert all(f == FORM_CIRCLE for f in history[1]['formes'])
    print("  --> [OK] Modèle 003 Validé.")
    
    # 4. Champ des Possibilités
    print("\n--- [CHAMP DES POSSIBILITÉS] Organisme de Possibilités ---")
    esp = Espace()
    b = Bloc("Init", forme=FORM_CIRCLE)
    esp.add_bloc_libre(b)
    field = PossibilityField(esp)
    print(field.summary())
    metrics = field.coverage_metrics()
    assert metrics['known_states_count'] >= 1
    print("  --> [OK] Champ des Possibilités Validé.")

if __name__ == "__main__":
    test_models_plan()
