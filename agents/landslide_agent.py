import os
import joblib
from strands import Agent, LLM
from agents.tools.imd_weather_tool import get_imd_weather_telemetry
from agents.tools.satellite_sensor_tool import get_satellite_sensor_data
from agents.tools.opensearch_geo_tool import query_local_infrastructure
from agents.tools.alert_generator_tool import generate_multilingual_alert

# Determine Model Path for heuristics
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml/model_weights.joblib")

class FallbackHeuristic:
    """
    Automatic deterministic heuristic fallback so the agent runs 100% offline 
    even without local LLM access.
    """
    @staticmethod
    def evaluate(district: str, lat: float, lon: float):
        print("Using Deterministic Heuristic Fallback...")
        weather = get_imd_weather_telemetry(district)
        sat_data = get_satellite_sensor_data(lat, lon)
        infra = query_local_infrastructure(lat, lon, 5.0)
        
        # Load RF model
        try:
            model = joblib.load(MODEL_PATH)
            # Dummy features for the model based on telemetry
            # [ARI, Factor of Safety, InSAR velocity, soil moisture]
            X = [[weather["cum_72h"], 0.9, sat_data["insar_velocity_mm_yr"], sat_data["soil_moisture_percentage"]]]
            pred = model.predict(X)[0]
        except Exception as e:
            print(f"Model error: {e}, falling back to static rules")
            pred = 1 if weather["warning"] == "Red" else 0
            
        risk = "HIGH" if pred == 1 else "LOW"
        
        corridor = infra.get("affected_corridors", ["Unknown"])[0] if infra.get("affected_corridors") else "Unknown"
        alerts = generate_multilingual_alert(district, risk, corridor)
        
        return {
            "risk_assessment": risk,
            "directives": f"Dispatch field teams to {corridor}.",
            "alerts": alerts
        }

def run_landslide_agent(district: str, lat: float, lon: float):
    # Try using Strands with local LLM
    try:
        # Local Ollama endpoint setup
        llm = LLM(
            model="llama3", 
            base_url="http://localhost:11434/v1",
            api_key="ollama" # Mock key for local Ollama
        )
        
        agent = Agent(
            llm=llm,
            tools=[
                get_imd_weather_telemetry, 
                get_satellite_sensor_data, 
                query_local_infrastructure, 
                generate_multilingual_alert
            ],
            system_prompt=(
                "You are an expert landslide risk assessment agent working for NER. "
                "You assess risk using weather, satellite data, and infrastructure queries. "
                "You must return actionable directives and generate multilingual alerts."
            )
        )
        
        prompt = f"Assess landslide risk for district {district} at coords ({lat}, {lon})."
        response = agent.run(prompt)
        return response
    except Exception as e:
        print(f"Local LLM not reachable or failed: {e}")
        return FallbackHeuristic.evaluate(district, lat, lon)

if __name__ == "__main__":
    # Test execution
    res = run_landslide_agent("Kohima", 25.6751, 94.1086)
    print("Agent Result:")
    print(res)
