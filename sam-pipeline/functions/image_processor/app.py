import json
import os
import boto3
from PIL import Image, ExifTags
import io

# Use host.docker.internal for SAM local invocation to reach LocalStack
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://host.docker.internal:4566")

s3_client = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT, region_name="us-east-1")

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    decimal = float(degrees) + float(minutes)/60 + float(seconds)/(3600)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_exif_gps(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif = image._getexif()
        if not exif:
            return None
        
        gps_info = {}
        for key, val in exif.items():
            decode = ExifTags.TAGS.get(key, key)
            if decode == "GPSInfo":
                for t in val:
                    sub_decoded = ExifTags.GPSTAGS.get(t, t)
                    gps_info[sub_decoded] = val[t]
        
        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info.get('GPSLatitudeRef', 'N'))
            lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info.get('GPSLongitudeRef', 'E'))
            return {"lat": round(lat, 6), "lon": round(lon, 6)}
        return None
    except Exception as e:
        print(f"Error extracting EXIF: {e}")
        return None

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    results = []
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        try:
            # Download image from S3 (LocalStack)
            response = s3_client.get_object(Bucket=bucket, Key=key)
            image_bytes = response['Body'].read()
            
            # Extract GPS
            gps = extract_exif_gps(image_bytes)
            
            result = {
                "report_id": key.split('.')[0],
                "bucket": bucket,
                "key": key,
                "gps": gps,
                "timestamp": record['eventTime']
            }
            results.append(result)
            print(f"Processed {key}: {gps}")
            
            # Here you would typically push this to OpenSearch or a backend API
            # For demonstration, we just return it.
            
        except Exception as e:
            print(f"Error processing object {key} from bucket {bucket}. Event: {json.dumps(event)}")
            print(e)
            
    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }
