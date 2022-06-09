from contextlib import contextmanager
import os
import tempfile
from backend.common.storage.settings import settings
import boto3
from botocore.client import Config
from botocore.errorfactory import ClientError
from backend.common.core.config import config


class DocumentStorageClient:
    def __init__(self):
        
        if config["is_local"]:
            self.s3 = boto3.resource(
                "s3",
                endpoint_url=settings.endpoint_url,
                aws_access_key_id = config["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key = config["AWS_SECRET_ACCESS_KEY"],
                config=Config(signature_version="s3v4"),
                region_name = config["AWS_REGION"]
            )
        else:
            self.s3 = boto3.resource(
                "s3",
                endpoint_url=settings.endpoint_url,
                config=Config(signature_version="s3v4"),
            )

        self.bucket = self.s3.Bucket(settings.document_bucket)

        if not self.bucket.creation_date:
            self.bucket.create()

    def get_full_path(self, document_name):
        return f"{settings.document_path}/{document_name}"

    def write_document(self, document_name, temp_document_path):
        self.bucket.upload_file(
            Filename=temp_document_path,
            Key=self.get_full_path(document_name),
            ExtraArgs={"ContentType": "application/pdf"},
        )

    def read_document(self, document_name):
        return self.read_document_stream(document_name).read()

    @contextmanager
    def read_document_to_tempfile(self, document_name):
        with tempfile.NamedTemporaryFile() as temp:
            doc = self.read_document(document_name)
            temp.write(doc)
            yield temp.name

    def read_document_stream(self, document_name):
        return self.bucket.Object(self.get_full_path(document_name)).get()["Body"]

    def document_exists(self, document_name):
        try:
            self.bucket.Object(self.get_full_path(document_name)).load()
            return True
        except ClientError as ex:
            return False
