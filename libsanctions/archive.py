import os
import json
import logging
import boto3

from libsanctions.config import AWS_BUCKET, AWS_ACCESS_KEY_ID
from libsanctions.config import AWS_SECRET_ACCESS_KEY

log = logging.getLogger(__name__)

LATEST = 'latest'
CSV_FORMAT = 'v1/sources/%s/%s/%s'
JSON_FORMAT = 'v1/entities/%s/%s'


def get_bucket():
    if AWS_SECRET_ACCESS_KEY is None:
        log.warning("No $AWS_SECRET_ACCESS_KEY defined, skipping upload.")
        return None
    s3 = boto3.resource(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    return s3.Bucket(AWS_BUCKET)


def upload_csv(bucket, source, run, file_path):
    file_name = os.path.basename(file_path)
    key_name = CSV_FORMAT % (source, run, file_name)
    log.info("Uploading [%s]: %s", AWS_BUCKET, key_name)
    args = {
        'ContentType': 'text/csv',
        'ACL': 'public-read',
    }
    obj = bucket.Object(key_name)
    obj.upload_file(file_path, ExtraArgs=args)
    copy_name = CSV_FORMAT % (source, LATEST, file_name)
    copy_source = {'Key': key_name, 'Bucket': AWS_BUCKET}
    bucket.copy(copy_source, copy_name, ExtraArgs=args)


def upload_entity(bucket, entity):
    key_name = JSON_FORMAT % (entity.source, entity.id)
    obj = bucket.Object(key_name)
    obj.put(ACL='public-read', ContentType='application/json',
            Body=json.dumps(entity.to_json()))
