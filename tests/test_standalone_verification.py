import unittest
import os
import sys

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.landslide_predictor import LandslidePredictor
from policies.policy_evaluator import CedarEvaluator
from backend.app.services.priority_engine import PriorityEngine


class TestMLPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = LandslidePredictor()

    def test_ari_calculation(self):
        # ARI = R0 + 0.8*R1 + 0.5*R2
        ari = self.predictor.calculate_ari(50.0, 30.0, 20.0)
        self.assertAlmostEqual(ari, 50.0 + 0.8 * 30.0 + 0.5 * 20.0)

    def test_fs_calculation(self):
        # Factor of Safety calculation
        fs = self.predictor.calculate_fs(
            slope_angle_deg=35.0,
            soil_saturation_pct=75.0,
            cohesion_kpa=15.0,
            friction_angle_deg=28.0,
            slip_depth_m=2.0
        )
        self.assertIsInstance(fs, float)
        self.assertGreater(fs, 0.0)

    def test_predict_risk(self):
        result = self.predictor.predict_risk(
            r0=80.0,
            r1=60.0,
            r2=40.0,
            slope_angle_deg=40.0,
            soil_saturation_pct=85.0,
            cohesion_kpa=10.0,
            friction_angle_deg=25.0,
            slip_depth_m=2.5,
            fissure_depth_cm=15.0,
            elevation=1800.0
        )
        self.assertIn("antecedent_rainfall_index", result)
        self.assertIn("factor_of_safety", result)
        self.assertIn("physical_risk_level", result)
        self.assertIn("ml_risk_level", result)
        self.assertIn(result["ml_risk_level"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])


class TestCedarAuthorization(unittest.TestCase):
    def setUp(self):
        self.evaluator = CedarEvaluator()

    def test_citizen_can_submit_report(self):
        res = self.evaluator.evaluate(
            principal='User::"citizen_alice"',
            action='Action::"SubmitHazardReport"',
            resource='HazardReport::"rep-001"'
        )
        self.assertIn(res["decision"], ["ALLOW", "Allow"])

    def test_citizen_cannot_update_road_status(self):
        res = self.evaluator.evaluate(
            principal='User::"citizen_alice"',
            action='Action::"UpdateRoadStatus"',
            resource='RoadCorridor::"NH-29"'
        )
        self.assertIn(res["decision"], ["DENY", "Deny"])

    def test_inspector_can_verify_report(self):
        res = self.evaluator.evaluate(
            principal='User::"inspector_bob"',
            action='Action::"VerifyHazardReport"',
            resource='HazardReport::"rep-001"'
        )
        self.assertIn(res["decision"], ["ALLOW", "Allow"])

    def test_district_officer_can_update_road_and_alert(self):
        res_road = self.evaluator.evaluate(
            principal='User::"officer_kohima"',
            action='Action::"UpdateRoadStatus"',
            resource='RoadCorridor::"NH-29"'
        )
        self.assertIn(res_road["decision"], ["ALLOW", "Allow"])

        res_alert = self.evaluator.evaluate(
            principal='User::"officer_kohima"',
            action='Action::"DispatchRegionalAlert"',
            resource='SystemAlert::"alert-001"'
        )
        self.assertIn(res_alert["decision"], ["ALLOW", "Allow"])


class TestPriorityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PriorityEngine()

    def test_default_grid_connected(self):
        triage = self.engine.calculate_triage_priority()
        # In default state with OPEN roads, no settlements should be isolated
        self.assertEqual(len(triage), 0)

    def test_road_blockage_triggers_isolation(self):
        # Block NH-29
        self.engine.update_road_status("NH-29-NAGALAND", "BLOCKED")
        triage = self.engine.calculate_triage_priority(days_isolated={"Kohima": 3, "Zubza": 3})
        self.assertGreater(len(triage), 0)
        isolated_names = [item["settlement"] for item in triage]
        self.assertIn("Kohima", isolated_names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
