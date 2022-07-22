import logging
import os
import tempfile
import boto3
from contextlib import contextmanager
from pathlib import Path
from backend.common.storage.settings import settings
from botocore.client import Config
from botocore.errorfactory import ClientError
from backend.common.core.config import config, is_local


class BaseS3Client:
    root_path = ""
    extra_args = {}

    def __init__(self):
        if is_local:
            self.s3 = boto3.resource(
                "s3",
                endpoint_url=settings.endpoint_url,
                aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"],
                config=Config(signature_version="s3v4"),
            )
        else:
            self.s3 = boto3.resource(
                "s3",
                config=Config(signature_version="s3v4"),
            )

        self.bucket = self.s3.Bucket(settings.document_bucket)

        if not self.bucket.creation_date:
            self.bucket.create()

    def get_full_path(self, relative_key):
        logging.info(f"client root_path={self.root_path}")
        return str(Path(self.root_path).joinpath(relative_key))

    def write_object(
        self,
        relative_key,
        temp_object_path,
        content_type: str | None = "application/pdf",  # TODO rxnormlinker
    ):
        self.bucket.upload_file(
            Filename=temp_object_path,
            Key=self.get_full_path(relative_key),
            ExtraArgs={"ContentType": content_type},
        )

    def write_object_mem(self, relative_key: str, object: bytes) -> None:
        self.bucket.put_object(Key=self.get_full_path(relative_key), Body=object)

    def download_directory(self, relative_prefix, local_path):
        prefix = self.get_full_path(relative_prefix)
        nopref_prefix = prefix.removeprefix("/")
        for obj in self.bucket.objects.filter(Prefix=prefix):
            nopref_key = obj.key.removeprefix("/")
            rel_prefix = nopref_key.removeprefix(nopref_prefix).removeprefix("/")
            rel_path = os.path.join(local_path, rel_prefix)
            if not os.path.exists(os.path.dirname(rel_path)):
                os.makedirs(os.path.dirname(rel_path))
            self.bucket.download_file(obj.key, str(rel_path))

    def read_object(self, relative_key):
        return self.read_object_stream(relative_key).read()

    @contextmanager
    def read_object_to_tempfile(self, relative_key):
        with tempfile.NamedTemporaryFile() as temp:
            doc = self.read_object(relative_key)
            temp.write(doc)
            yield temp.name

    def read_object_stream(self, relative_key):
        return self.bucket.Object(self.get_full_path(relative_key)).get()["Body"]

    def read_lines(self, relative_key):
        for line in self.read_object_stream(relative_key).iter_lines():
            yield line.decode("utf-8")

    def object_exists(self, relative_key):
        try:
            self.bucket.Object(self.get_full_path(relative_key)).load()
            return True
        except ClientError as ex:
            return False

    def get_signed_url(self, relative_key, expires_in_seconds=60):
        logging.info(f"relative_key={relative_key}")
        key = self.get_full_path(relative_key)
        logging.info(f"Key={key} Bucket={settings.document_bucket}")
        return self.s3.meta.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.document_bucket,
                "Key": key,
            },
            ExpiresIn=expires_in_seconds,
        )


class ModelStorageClient(BaseS3Client):
    root_path = settings.model_path


class DocumentStorageClient(BaseS3Client):
    root_path = settings.document_path


class TextStorageClient(BaseS3Client):
    root_path = settings.text_path


class DiffStorageClient(BaseS3Client):
    root_path = settings.diff_path
