from opensearchpy import OpenSearch
from app.config import settings

# Initialize OpenSearch client
client = OpenSearch(
    hosts=[settings.OPENSEARCH_HOST],
    use_ssl=False,
    verify_certs=False,
)

def check_opensearch_health():
    try:
        return client.ping()
    except Exception:
        return False

def get_recent_hazards(limit=50):
    query = {
        "size": limit,
        "query": {
            "match_all": {}
        },
        "sort": [
            {"timestamp": {"order": "desc"}}
        ]
    }
    try:
        res = client.search(index="hazard_reports", body=query)
        return [hit["_source"] for hit in res["hits"]["hits"]]
    except Exception as e:
        print(f"Error fetching hazards: {e}")
        return []

def get_risk_zones():
    query = {
        "size": 100,
        "query": {
            "match_all": {}
        }
    }
    try:
        res = client.search(index="risk_zones", body=query)
        return [{"id": hit["_id"], **hit["_source"]} for hit in res["hits"]["hits"]]
    except Exception as e:
        print(f"Error fetching risk zones: {e}")
        return []

def update_corridor_status(corridor_id: str, status: str):
    # In a real scenario, we would use update by query or direct update if ID matches corridor_id
    query = {
        "query": {
            "term": {
                "corridor_id": corridor_id
            }
        }
    }
    try:
        res = client.search(index="risk_zones", body=query)
        if not res["hits"]["hits"]:
            return False
        
        doc_id = res["hits"]["hits"][0]["_id"]
        client.update(index="risk_zones", id=doc_id, body={"doc": {"status": status}})
        client.indices.refresh(index="risk_zones")
        return True
    except Exception as e:
        print(f"Error updating corridor: {e}")
        return False
        
def store_hazard_report(report_data: dict):
    try:
        client.index(index="hazard_reports", body=report_data)
        client.indices.refresh(index="hazard_reports")
        return True
    except Exception as e:
        print(f"Error storing hazard report: {e}")
        return False
