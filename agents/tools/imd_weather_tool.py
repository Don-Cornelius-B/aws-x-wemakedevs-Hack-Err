from strands import tool

@tool
def get_imd_weather_telemetry(district: str) -> dict:
    """
    Fetch IMD weather telemetry for NER districts (Kohima, Gangtok, Shillong, Champhai).
    Provides district-level precipitation rates (mm/h), cumulative 24h/48h/72h rainfall, 
    and IMD color-coded warnings (Yellow/Orange/Red).
    """
    mock_data = {
        "Kohima": {"precip_mm_h": 25.4, "cum_24h": 120, "cum_48h": 250, "cum_72h": 310, "warning": "Red"},
        "Gangtok": {"precip_mm_h": 12.0, "cum_24h": 45, "cum_48h": 90, "cum_72h": 140, "warning": "Orange"},
        "Shillong": {"precip_mm_h": 35.0, "cum_24h": 150, "cum_48h": 280, "cum_72h": 400, "warning": "Red"},
        "Champhai": {"precip_mm_h": 5.0, "cum_24h": 20, "cum_48h": 40, "cum_72h": 60, "warning": "Yellow"}
    }
    
    return mock_data.get(district.title(), {
        "precip_mm_h": 0.0, 
        "cum_24h": 0, 
        "cum_48h": 0, 
        "cum_72h": 0, 
        "warning": "None"
    })
