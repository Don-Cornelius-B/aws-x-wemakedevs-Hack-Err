import json
import os
import time
from opensearchpy import OpenSearch, helpers

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://localhost:9200")

client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    use_ssl=False,
    verify_certs=False,
)

def wait_for_opensearch():
    for _ in range(30):
        try:
            if client.ping():
                print("OpenSearch is up!")
                return
        except Exception:
            pass
        print("Waiting for OpenSearch...")
        time.sleep(2)
    raise Exception("OpenSearch did not start in time.")

def create_index(index_name, mapping_file):
    if client.indices.exists(index=index_name):
        print(f"Index {index_name} already exists. Deleting it.")
        client.indices.delete(index=index_name)
    
    with open(mapping_file, "r") as f:
        mapping = json.load(f)
    
    client.indices.create(index=index_name, body=mapping)
    print(f"Created index {index_name}.")

def seed_data():
    risk_zones = [
        {
            "_index": "risk_zones",
            "_source": {
                "corridor_id": "NH-29-NAGALAND",
                "name": "Kohima-Dimapur Corridor (Pagla Pahar)",
                "highway": "NH-29",
                "status": "OPEN",
                "risk_level": "MEDIUM",
                "settlements_served": ["Kohima", "Dimapur", "Zubza", "Medziphema"],
                "geometry": {
                    "type": "linestring",
                    "coordinates": [
                        [93.73, 25.82],
                        [93.85, 25.75],
                        [94.02, 25.71],
                        [94.10, 25.67]
                    ]
                }
            }
        },
        {
            "_index": "risk_zones",
            "_source": {
                "corridor_id": "NH-10-SIKKIM",
                "name": "Sevoke-Gangtok Corridor (Teesta Valley)",
                "highway": "NH-10",
                "status": "COMPROMISED",
                "risk_level": "HIGH",
                "settlements_served": ["Gangtok", "Singtam", "Rangpo", "Teesta Bazaar"],
                "geometry": {
                    "type": "linestring",
                    "coordinates": [
                        [88.42, 26.89],
                        [88.48, 27.05],
                        [88.52, 27.18],
                        [88.61, 27.33]
                    ]
                }
            }
        },
        {
             "_index": "risk_zones",
             "_source": {
                 "corridor_id": "EKH-MEGHALAYA",
                 "name": "Shillong-Cherrapunji Corridor",
                 "highway": "SH-5",
                 "status": "OPEN",
                 "risk_level": "LOW",
                 "settlements_served": ["Shillong", "Mylliem", "Mawkdok", "Cherrapunji"],
                 "geometry": {
                     "type": "linestring",
                     "coordinates": [
                         [91.89, 25.57],
                         [91.81, 25.43],
                         [91.73, 25.33],
                         [91.73, 25.28]
                     ]
                 }
             }
        }
    ]

    hazard_reports = [
        {
            "_index": "hazard_reports",
            "_source": {
                "report_id": "rep-001",
                "location": {"lat": 25.75, "lon": 93.85},
                "reporter_role": "Citizen",
                "fissure_depth_cm": 15.5,
                "soil_type": "weathered_sandstone",
                "verified": False,
                "severity": 3,
                "photo_s3_key": "photos/rep-001.jpg",
                "timestamp": "2026-09-17T08:30:00Z"
            }
        },
        {
            "_index": "hazard_reports",
            "_source": {
                "report_id": "rep-002",
                "location": {"lat": 27.18, "lon": 88.52},
                "reporter_role": "FieldInspector",
                "fissure_depth_cm": 45.0,
                "soil_type": "phyllite",
                "verified": True,
                "severity": 5,
                "photo_s3_key": "photos/rep-002.jpg",
                "timestamp": "2026-09-18T10:15:00Z"
            }
        }
    ]

    helpers.bulk(client, risk_zones + hazard_reports)
    print(f"Seeded {len(risk_zones)} risk zones and {len(hazard_reports)} hazard reports.")
    client.indices.refresh(index="risk_zones")
    client.indices.refresh(index="hazard_reports")

if __name__ == "__main__":
    wait_for_opensearch()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    create_index("hazard_reports", os.path.join(script_dir, "indices", "hazard_reports_mapping.json"))
    create_index("risk_zones", os.path.join(script_dir, "indices", "risk_zones_mapping.json"))
    
    seed_data()
