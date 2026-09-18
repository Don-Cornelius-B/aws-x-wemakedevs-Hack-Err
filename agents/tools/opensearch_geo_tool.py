from strands import tool
from opensearchpy import OpenSearch
import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://localhost:9200")
client = OpenSearch(hosts=[OPENSEARCH_HOST], use_ssl=False, verify_certs=False)

@tool
def query_local_infrastructure(lat: float, lon: float, radius_km: float) -> dict:
    """
    Query the local OpenSearch cluster for road segments, critical facilities, 
    and settlements within a hazard buffer.
    """
    try:
        query = {
            "query": {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {
                        "geo_distance": {
                            "distance": f"{radius_km}km",
                            "location": {
                                "lat": lat,
                                "lon": lon
                            }
                        }
                    }
                }
            }
        }
        # We mock the response if OS is not available during offline agent execution
        try:
            res = client.search(index="risk_zones", body=query)
            hits = res["hits"]["hits"]
            corridors = [h["_source"].get("corridor_id") for h in hits]
            return {"affected_corridors": corridors, "critical_facilities": len(hits)}
        except Exception:
            return {"affected_corridors": ["NH-29-NAGALAND"], "critical_facilities": 1, "note": "OS uncontactable, using mock"}
            
    except Exception as e:
        return {"error": str(e)}
