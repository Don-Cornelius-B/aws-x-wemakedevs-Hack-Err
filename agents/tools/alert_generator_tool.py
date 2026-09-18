from strands import tool

@tool
def generate_multilingual_alert(district: str, risk_level: str, affected_corridor: str) -> dict:
    """
    Generate culturally contextualized early warning broadcasts across three languages: 
    English, Assamese (অসমীয়া), and Bengali (বাংলা).
    """
    if risk_level.lower() == "red" or risk_level.lower() == "high":
        en = f"EMERGENCY: High landslide risk in {district}. Evacuate {affected_corridor} immediately."
        as_ = f"জৰুৰীকালীন: {district}ত ভূমিস্খলনৰ উচ্চ বিপদ। লগে লগে {affected_corridor} খালী কৰক।"
        bn = f"জরুরী: {district} এ ভূমিধসের উচ্চ ঝুঁকি। অবিলম্বে {affected_corridor} খালি করুন।"
    elif risk_level.lower() == "orange" or risk_level.lower() == "medium":
        en = f"WARNING: Moderate landslide risk in {district}. Avoid travel on {affected_corridor}."
        as_ = f"সতৰ্কবাণী: {district}ত মজলীয়া ভূমিস্খলনৰ বিপদ। {affected_corridor}ত ভ্ৰমণৰ পৰা বিৰত থাকক।"
        bn = f"সতর্কতা: {district} এ মাঝারি ভূমিধসের ঝুঁকি। {affected_corridor} এ যাতায়াত এড়িয়ে চলুন।"
    else:
        en = f"INFO: Normal conditions in {district}. Stay safe."
        as_ = f"তথ্য: {district}ত স্বাভাৱিক অৱস্থা। নিৰাপদে থাকক।"
        bn = f"তথ্য: {district} এ স্বাভাবিক অবস্থা। নিরাপদে থাকুন।"
        
    return {
        "en": en,
        "as": as_,
        "bn": bn
    }
