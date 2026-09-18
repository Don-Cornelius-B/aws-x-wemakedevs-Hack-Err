import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def create_and_save_model():
    # Synthetic data features: [ARI, Factor of Safety, InSAR velocity, soil moisture]
    # Simulating geotechnical slope parameters
    np.random.seed(42)
    X = np.random.rand(1000, 4) * [100, 2, 50, 100]  
    
    # High ARI, low FS, high InSAR, high moisture -> failure (1)
    y = np.where((X[:, 0] > 70) | (X[:, 1] < 1.0) | (X[:, 2] > 20) | (X[:, 3] > 60), 1, 0)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    output_path = os.path.join(os.path.dirname(__file__), 'model_weights.joblib')
    joblib.dump(model, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    create_and_save_model()
