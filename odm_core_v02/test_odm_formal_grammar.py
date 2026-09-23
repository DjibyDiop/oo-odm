"""
OO-ODM — Organique des Matières
odm_core_v02/test_odm_formal_grammar.py : Validation de la Grammaire Opérationnelle Formelle

Certification des 3 piliers fondateurs (plan.md) :
  1. Table normative des 7 Opérations et Transitions d'état Sₜ ──OP──→ Sₜ₊₁
  2. Résultat formel Q ∈ {E, R, O, T, Π, ★} et Dépendance Contextuelle
  3. Système de Lois, Conditions et Stabilité (Lois I, II, III & Invariants)
  4. Métrologie Organique (Profondeur, Distance, Richesse d'Émergence)
  5. Validation Native D+ (OdMGrammarOrgan via dpc.exe et graphe OPI)

RÈGLE ABSOLUE : ZÉRO MOCKS.
"""

import os
import sys
import copy
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odm_core_v02.odm.element import Element, CIRCLE, TRIANGLE, SQUARE, STAR
from odm_core_v02.odm.engine import OdMCore
from odm_core_v02.odm.grammar import (
    OperationalGrammar,
    OperationalContext,
    ResultQType,
    ResultQ,
    StateTransition
)
from odm_core_v02.odm.laws import (
    LawsOfMatter,
    StabilityEvaluator,
    StabilityRegime,
    Condition,
    ConditionType
)
from odm_core_v02.odm.metrics import (
    OrganicMetrics,
    OrganicMeasurement
)
from omx.oir import OIRInstruction, OIRType
from omx.o_dplus import ODPlusEngine


class TestODMformalGrammar(unittest.TestCase):

    def setUp(self):
        """Initialisation d'un espace OdM propre avec les formes canoniques."""
        self.odm = OdMCore()
        self.odm.add_element("A", CIRCLE, {"energie": 100})
        self.odm.elements["A"].state["vitalite"] = "forte"
        self.odm.add_element("B", TRIANGLE, {"energie": 80})
        self.odm.elements["B"].state["direction"] = "nord"
        self.odm.add_element("C", SQUARE, {"energie": 120})
        self.odm.elements["C"].state["stabilite"] = "haute"
        self.grammar = OperationalGrammar()

    def test_01_normative_seven_operations(self):
        """1. Validation normative des 7 opérations fondamentales produisant Q."""
        print("\n[TEST 1] Validation de la table normative des 7 opérations fondamentales...")

        # 1. LIAISON : L(A, B | ctx) ──→ Q_RELATION
        res_l = self.grammar.apply_liaison(self.odm, "A", "B")
        self.assertEqual(res_l.q_type, ResultQType.RELATION)
        self.assertIn("R(A, B)", res_l.description)
        rel_id = next(iter(self.odm.relations.keys()))
        print(f"  ✓ 1. LIAISON : {res_l}")

        # 2. RUPTURE : R(rel_id | ctx) ──→ Q_RELATION
        res_r = self.grammar.apply_rupture(self.odm, rel_id)
        self.assertEqual(res_r.q_type, ResultQType.RELATION)
        self.assertIn("Rupture", res_r.description)
        print(f"  ✓ 2. RUPTURE : {res_r}")

        # 3. TRANSFORMATION : T(A, Δ | ctx) ──→ Q_TRANSFORMATION / Q_ELEMENT
        delta = {"content": {"energie": 250}, "state": {"vitalite": "excitee"}}
        res_t = self.grammar.apply_transformation(self.odm, "A", delta)
        self.assertEqual(res_t.q_type, ResultQType.TRANSFORMATION)
        self.assertEqual(self.odm.elements["A"].content["energie"], 250)
        print(f"  ✓ 3. TRANSFORMATION : {res_t}")

        # 4. COMPOSITION : C(A, B, C | ctx) ──→ Q_ORGANISATION
        res_c = self.grammar.apply_composition(self.odm, ["A", "B", "C"], name="Trinite_Primaire")
        self.assertEqual(res_c.q_type, ResultQType.ORGANISATION)
        self.assertTrue(res_c.is_emergence)  # Ordre ≥ 3 engendre une émergence
        print(f"  ✓ 4. COMPOSITION : {res_c}")

        # 5. CONTENIR : CT(C, B | ctx) ──→ Q_ORGANISATION
        res_ct = self.grammar.apply_contenir(self.odm, "C", "B")
        self.assertEqual(res_ct.q_type, ResultQType.ORGANISATION)
        self.assertIn("B", self.odm.elements["C"].state.get("contains", []))
        print(f"  ✓ 5. CONTENIR : {res_ct}")

        # 6. DIVISION : D(C, mode='partition' | ctx) ──→ Q_ELEMENT
        res_d = self.grammar.apply_division(self.odm, "C", mode="partition", new_ids=["C1", "C2"])
        self.assertEqual(res_d.q_type, ResultQType.ELEMENT)
        self.assertIn("C1", self.odm.elements)
        self.assertIn("C2", self.odm.elements)
        print(f"  ✓ 6. DIVISION : {res_d}")

        # 7. CARACTÉRISATION : K(A | ctx) ──→ Q_TRANSFORMATION
        res_k = self.grammar.apply_caracterisation(self.odm, "A")
        self.assertEqual(res_k.q_type, ResultQType.TRANSFORMATION)
        self.assertIn("A", res_k.metadata["target_id"])
        print(f"  ✓ 7. CARACTÉRISATION : {res_k}")

    def test_02_formal_transitions_and_context(self):
        """2. Validation des transitions Sₜ ──OP──→ Sₜ₊₁ et de l'effet de contexte."""
        print("\n[TEST 2] Validation des transitions formelles et de l'influence du contexte...")

        ctx = OperationalContext.from_engine(self.odm)
        self.assertEqual(ctx.environment["atp_available"], 1000)
        self.assertEqual(ctx.forms["A"], CIRCLE)
        self.assertEqual(ctx.forms["B"], TRIANGLE)

        # Exécution de transition auditée
        trans = self.grammar.execute_transition(
            self.odm,
            operation="LIAISON",
            targets=["A", "C"],
            context=ctx
        )

        self.assertIsInstance(trans, StateTransition)
        self.assertEqual(trans.operation_name, "LIAISON")
        self.assertEqual(trans.delta_relations, 1)
        self.assertEqual(trans.atp_consumed, 10)
        self.assertEqual(ctx.environment["atp_available"], 990)
        self.assertTrue(trans.invariants_valid)
        self.assertNotEqual(trans.state_before_hash, trans.state_after_hash)

        print(f"  ✓ Transition auditée : {trans.summary()}")

    def test_03_laws_of_matter_and_stability(self):
        """3. Validation du système de lois, conditions et évaluation de la stabilité."""
        print("\n[TEST 3] Validation des lois fondamentales et de la stabilité...")

        # Loi I : Conservation de l'énergie
        v_ok = LawsOfMatter.check_law_conservation("DIVISION", atp_cost=30, available_atp=100)
        self.assertTrue(v_ok.allowed)

        v_fail = LawsOfMatter.check_law_conservation("DIVISION", atp_cost=150, available_atp=50)
        self.assertFalse(v_fail.allowed)
        print(f"  ✓ Loi I (Conservation ATP) : {v_ok.explanation} / Rejet: {v_fail.explanation}")

        # Loi II : Affinité morphologique
        affinity_ct = LawsOfMatter.get_morphological_affinity(CIRCLE, TRIANGLE)
        self.assertGreaterEqual(affinity_ct, 0.90)  # Synergie forte
        v_morpho = LawsOfMatter.check_law_morphology(CIRCLE, TRIANGLE)
        self.assertTrue(v_morpho.allowed)
        print(f"  ✓ Loi II (Affinité morphologique ○–△) : {v_morpho.explanation}")

        # Évaluation de la stabilité intrinsèque
        stab_a = StabilityEvaluator.evaluate_element(self.odm.elements["A"])
        self.assertEqual(stab_a.regime, StabilityRegime.STABLE)
        self.assertGreater(stab_a.coherence_index, 0.8)

        star_elem = Element("S1", STAR, {"energie": 400})
        stab_star = StabilityEvaluator.evaluate_element(star_elem)
        self.assertEqual(stab_star.regime, StabilityRegime.METASTABLE)
        print(f"  ✓ Stabilité intrinsèque : A={stab_a.regime.value}, S1={stab_star.regime.value} ({stab_star.diagnostic})")

    def test_04_organic_metrics_and_depth(self):
        """4. Validation de la métrologie organique (profondeur, distance, richesse)."""
        print("\n[TEST 4] Validation des mesures organiques (profondeur, distance, entropie)...")

        # État initial
        state_0 = copy.deepcopy(self.odm.to_dict())

        # Création d'une transformation et d'une organisation
        self.grammar.apply_liaison(self.odm, "A", "B")
        self.grammar.apply_composition(self.odm, ["A", "B"], name="Duo")
        state_1 = copy.deepcopy(self.odm.to_dict())

        # Mesure de distance organique D(S₀, S₁)
        dist = OrganicMetrics.compute_organic_distance(state_0, state_1)
        self.assertGreater(dist, 0.0)
        print(f"  ✓ Distance organique D(S₀, S₁) = {dist:.3f}")

        # Mesure de profondeur
        max_d, avg_d = OrganicMetrics.compute_engine_depth(self.odm)
        self.assertGreaterEqual(max_d, 1)

        # Rapport de mesure complet
        measurement = OrganicMetrics.measure_full(self.odm, self.grammar)
        self.assertIsInstance(measurement, OrganicMeasurement)
        self.assertGreater(measurement.entropie_shannon, 0.0)
        print(f"  ✓ Mesure complète : {measurement.summary()}")

    def test_05_native_dplus_grammar_organ(self):
        """5. Validation de l'organe D+ natif OdMGrammarOrgan (Zéro Mocks via dpc.exe)."""
        print("\n[TEST 5] Validation de l'organe natif D+ OdMGrammarOrgan...")

        dplus_engine = ODPlusEngine()
        instr = OIRInstruction(OIRType.VALIDATE_GRAMMAR, {"source": "formal_grammar_test"})
        res = dplus_engine.process(instr)

        self.assertEqual(res.get("status"), "GRAMMAR_VALIDATED")
        self.assertEqual(res.get("organ"), "OdMGrammarOrgan")
        self.assertTrue(res.get("is_biologically_coherent"))
        self.assertGreaterEqual(res.get("graph_nodes_count", 0), 5)

        print(f"  ✓ Organe D+ OdMGrammarOrgan validé nativement :")
        print(f"    - Nœuds OPI : {res['graph_nodes_count']}")
        print(f"    - Signaux certifiés : {', '.join(res['signals_checked'])}")


def test_formal_grammar():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestODMformalGrammar)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    assert result.wasSuccessful(), "Échec de validation de la grammaire formelle OdM"


if __name__ == "__main__":
    unittest.main()
