import boto3
import json
import os

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

def lambda_handler(event, context):

    response = {
        "unattached_volumes": {
            "count": 0,
            "size": 0
        },
        "non_encrypted_volumes": {
            "count": 0,
            "size": 0
        },
        "non_encrypted_snapshots": {
            "count": 0
        }
    }

    volumes = ec2.describe_volumes()['Volumes']
    
    for volume in volumes:
        if volume['State'] == 'available':
            response["unattached_volumes"]["count"] += 1
            response["unattached_volumes"]["size"] += volume['Size']
        
        if volume['Encrypted'] == False:
            response["non_encrypted_volumes"]["count"] += 1
            response["non_encrypted_volumes"]["size"] += volume['Size']

    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    for snapshot in snapshots:
        if snapshot['Encrypted'] == False:
            response["non_encrypted_snapshots"]["count"] += 1

    bucket_name = os.environ['BUCKET_NAME']
    
    response_json = json.dumps(response)

    s3.put_object(
        Bucket=bucket_name,
        Key='metrics_output.json',
        Body=response_json,
        ServerSideEncryption='AES256'
    )

    return response
