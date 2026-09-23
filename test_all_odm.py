"""
OO-ODM Unified Test Runner
Validates 100% of MEO and OMX modules under the Zero-Mocks policy.
"""
import sys
import os
import unittest
import importlib

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_odm_tests():
    print("==================================================")
    print("       OO-ODM UNIFIED SOVEREIGN TEST SUITE        ")
    print("==================================================")

    test_modules = [
        ("MEO Fondations", "meo.test_fondations_odm", "test_fondations"),
        ("MEO Laboratory", "meo.test_laboratory", "test_laboratory"),
        ("MEO v0.3 Constitution", "meo.test_meo_v03", "test_meo_v03"),
        ("MEO Modèles Canoniques (Plan.md)", "meo.test_models_plan", "test_models_plan"),
        ("OMX Moteurs Natifs (Zéro Mocks)", "omx.test_native_engines", "run_all_tests"),
        ("OMX OIR Lossless Serialization", "omx.test_oir_serialization", "test_oir_lossless_serialization"),
        ("OMX OIR IPC Corruption (Rust Native)", "omx.test_oir_ipc_corruption", "run_all_tests"),
        ("OMX Architecture Topology", "omx.test_omx", "test_omx_architecture"),
        ("OMX Multi-Trajectories (MT01)", "omx.test_omx_multitrajectories", "test_multitrajectories"),
        ("OMX Law Relaxation (MT02)", "omx.test_omx_mt02_relaxation", "test_mt02"),
        # --- Phase 2 : Moteur Organique Autonome ---
        ("OdM Expérience 001 (Séquence Canonique)", "odm_core_v02.test_experiment_001", "test_experiment_001"),
        ("OdM Expérience 002 (Boucle Autonome)", "odm_core_v02.test_experiment_002", "test_experiment_002"),
        ("OdM Expérience 003 (Machine de Découverte)", "odm_core_v02.test_experiment_003", "test_experiment_003"),
        # --- Phase 3 : Boucle Fermée OO ↔ OdM ---
        ("OdM Expérience 004 (Boucle Fermée OO↔OdM)", "odm_core_v02.test_experiment_004", "test_experiment_004"),
        # --- Phase 4 : Organisme de Possibilités ---
        ("OdM Expérience 005 (Organisme de Possibilités)", "odm_core_v02.test_experiment_005", "test_experiment_005"),
        # --- Phase 4 — Option 2 : Moteur OdM Intégral en pur D+ ---
        ("OdM Expérience 006 (Moteur Cœur D+ Natif — 7 Ops)", "odm_core_v02.test_odm_dplus_core", "test_odm_dplus_core"),
        # --- Phase 5 : Grammaire Opérationnelle Formelle & Métrologie ---
        ("OdM Grammaire Opérationnelle Formelle & Métrologie", "odm_core_v02.test_odm_formal_grammar", "test_formal_grammar"),
    ]


    passed = 0
    failed = 0

    for name, module_name, func_name in test_modules:
        print(f"\n--- [RUNNING] {name} ({module_name}.{func_name}) ---")
        try:
            mod = importlib.import_module(module_name)
            func = getattr(mod, func_name)
            func()
            print(f"--> [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"--> [FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n==================================================")
    print(f"   RESULTS: {passed} / {passed + failed} suites passed ({(passed * 100) // (passed + failed)}%)")
    print("==================================================")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_all_odm_tests())
