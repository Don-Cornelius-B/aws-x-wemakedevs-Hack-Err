from strands import tool

@tool
def get_satellite_sensor_data(lat: float, lon: float) -> dict:
    """
    Ingest simulated radar interferometry (InSAR) surface displacement velocities (mm/yr) 
    and ground IoT piezometer/soil moisture percentages for a given coordinate.
    """
    # Mock behavior depending on rough coordinate bounding
    insar_velocity = 15.5 # mm/yr displacement
    soil_moisture = 68.2 # percentage saturation
    
    # If in high risk pseudo-coord
    if lat > 26.0 and lon > 93.0:
        insar_velocity = 45.0
        soil_moisture = 85.0
        
    return {
        "insar_velocity_mm_yr": insar_velocity,
        "soil_moisture_percentage": soil_moisture,
        "piezometer_pressure_kpa": 120.5
    }
