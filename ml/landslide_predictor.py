import math
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os

class LandslidePredictor:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "model_weights.joblib")
        # Load model if it exists, else initialize a mock model
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.model = self._create_mock_model()

    def _create_mock_model(self):
        """Creates a simple mock model for testing purposes."""
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        # Features: [ARI, FS, fissure_depth_cm, slope_angle_deg, elevation]
        # Labels: 0 (Low), 1 (Medium), 2 (High/Critical)
        X_train = np.array([
            [10, 1.5, 0, 15, 1000],   # Low risk
            [50, 1.2, 5, 30, 1500],   # Medium risk
            [120, 0.8, 30, 45, 2000], # High risk
            [150, 0.6, 50, 60, 2500]  # Critical risk
        ])
        y_train = np.array([0, 1, 2, 2])
        model.fit(X_train, y_train)
        # Ensure directory exists before saving
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(model, self.model_path)
        return model

    def calculate_ari(self, r0: float, r1: float, r2: float) -> float:
        """
        Calculates the Antecedent Rainfall Index (ARI).
        ARI = R_0 + 0.8 * R_1 + 0.5 * R_2
        where R_n is the rainfall (in mm) n days prior.
        """
        return r0 + 0.8 * r1 + 0.5 * r2

    def calculate_fs(self, slope_angle_deg: float, soil_saturation_pct: float, 
                     cohesion_kpa: float, friction_angle_deg: float, 
                     slip_depth_m: float, total_unit_weight_kn_m3: float = 19.0) -> float:
        """
        Calculates the Infinite Slope Stability Factor of Safety (FS).
        FS = (c' + (gamma - m * gamma_w) * z * cos^2(beta) * tan(phi')) / (gamma * z * sin(beta) * cos(beta))
        """
        if slope_angle_deg <= 0 or slope_angle_deg >= 90:
            raise ValueError("Slope angle must be between 0 and 90 degrees exclusive.")
        if slip_depth_m <= 0:
            raise ValueError("Slip surface depth must be greater than 0.")
            
        beta_rad = math.radians(slope_angle_deg)
        phi_rad = math.radians(friction_angle_deg)
        gamma_w = 9.81 # unit weight of water in kN/m^3
        m = soil_saturation_pct / 100.0 # Saturation ratio (0 to 1)

        # Numerator components
        c_prime = cohesion_kpa
        effective_stress = (total_unit_weight_kn_m3 - m * gamma_w) * slip_depth_m * (math.cos(beta_rad) ** 2)
        frictional_resistance = effective_stress * math.tan(phi_rad)
        resisting_force = c_prime + frictional_resistance

        # Denominator components
        driving_force = total_unit_weight_kn_m3 * slip_depth_m * math.sin(beta_rad) * math.cos(beta_rad)

        if driving_force == 0:
            return float('inf')

        return resisting_force / driving_force

    def determine_risk_level(self, fs: float) -> str:
        """Maps FS to a risk level."""
        if fs < 1.0:
            return "CRITICAL" # >80% failure probability
        elif 1.0 <= fs <= 1.3:
            return "MEDIUM"
        else:
            return "LOW"

    def predict_risk(self, r0: float, r1: float, r2: float, 
                     slope_angle_deg: float, soil_saturation_pct: float, 
                     cohesion_kpa: float, friction_angle_deg: float, 
                     slip_depth_m: float, fissure_depth_cm: float = 0, elevation: float = 1000) -> dict:
        """
        Comprehensive risk prediction returning ARI, FS, categorical risk, 
        and ML model prediction probability.
        """
        ari = self.calculate_ari(r0, r1, r2)
        fs = self.calculate_fs(slope_angle_deg, soil_saturation_pct, cohesion_kpa, 
                               friction_angle_deg, slip_depth_m)
        physical_risk = self.determine_risk_level(fs)
        
        # Features: [ARI, FS, fissure_depth_cm, slope_angle_deg, elevation]
        features = np.array([[ari, fs, fissure_depth_cm, slope_angle_deg, elevation]])
        ml_prediction = int(self.model.predict(features)[0])
        ml_probs = self.model.predict_proba(features)[0].tolist()
        
        # Risk levels mapping: 0=LOW, 1=MEDIUM, 2=HIGH/CRITICAL
        ml_risk_map = {0: "LOW", 1: "MEDIUM", 2: "CRITICAL"}
        
        return {
            "antecedent_rainfall_index": round(ari, 2),
            "factor_of_safety": round(fs, 3),
            "physical_risk_level": physical_risk,
            "ml_risk_level": ml_risk_map.get(ml_prediction, "UNKNOWN"),
            "failure_probabilities": {
                "low": ml_probs[0] if len(ml_probs) > 0 else 0,
                "medium": ml_probs[1] if len(ml_probs) > 1 else 0,
                "high": ml_probs[2] if len(ml_probs) > 2 else 0
            }
        }
