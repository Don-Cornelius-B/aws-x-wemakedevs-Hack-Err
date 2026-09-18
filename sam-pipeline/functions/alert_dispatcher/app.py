import json
import os
import boto3
from pydantic import BaseModel, Field

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://host.docker.internal:4566")
QUEUE_URL = os.getenv("QUEUE_URL", f"{LOCALSTACK_ENDPOINT}/000000000000/ner-alert-notifications")

sqs_client = boto3.client('sqs', endpoint_url=LOCALSTACK_ENDPOINT, region_name="us-east-1")

class AlertPayload(BaseModel):
    district_id: str
    risk_level: str
    message_en: str
    message_as: str
    message_bn: str
    affected_corridors: list[str]

def lambda_handler(event, context):
    """
    Expects event payload representing an alert.
    Parses it and enqueues to SQS.
    """
    print("Received alert event:", json.dumps(event))
    
    try:
        # Validate payload
        if isinstance(event, str):
            event = json.loads(event)
            
        payload = AlertPayload(**event)
        
        # Publish to SQS
        sqs_response = sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=payload.model_dump_json(),
            MessageAttributes={
                'RiskLevel': {
                    'DataType': 'String',
                    'StringValue': payload.risk_level
                },
                'District': {
                    'DataType': 'String',
                    'StringValue': payload.district_id
                }
            }
        )
        
        print(f"Dispatched alert to SQS. MessageId: {sqs_response.get('MessageId')}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message_id": sqs_response.get('MessageId')
            })
        }
    except Exception as e:
        print(f"Error dispatching alert: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
