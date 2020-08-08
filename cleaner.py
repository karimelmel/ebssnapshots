from datetime import datetime
import boto3

def lambda_handler(event, context):
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName']
        for region in ec2_client.describe_regions()['Regions']]

    for region in regions:
        print("Region:", region)
        ec2 = boto3.client('ec2', region_name=region)

        response = ec2.describe_snapshots(OwnerIds=[account_id])
        snapshots = response["Snapshots"]

        #Sort snapshots ascending
        snapshots.sort(key=lambda x: x["StartTime"])

        #Remove last 5 snapshots that we want to keep from the list
        snapshots = snapshots[:-5]

        for snapshot in snapshots:
            id = snapshot['Snapshotid']
            try:
                print("Deleting snapshot:", id)
                ec2.delete_snapshot(SnapshotId=id)
            except Exception as e:
                if 'InvalidSnapshot.InUse' in e.message:
                    print("Snapshot {} in use.. skipping.".format(id))
                    continue
                
