import boto3


def client(region_name: str | None = None, endpoint_url: str | None = None):
    return boto3.client("s3", region_name=region_name, endpoint_url=endpoint_url)
