import logging
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

import aioboto3
import mypy_boto3_s3.service_resource as s3_resources
from aiofiles import os, tempfile
from aiopath import AsyncPath
from botocore.client import Config
from botocore.exceptions import ClientError


class AsyncS3Client:
    def __init__(
        self,
        root_path: str,
        resource: s3_resources.S3ServiceResource = None,
        stack: AsyncExitStack | None = None,
    ):
        self.resource = resource
        self.root_path = root_path
        self.stack = stack
        self.bucket: s3_resources.Bucket | None = None

    @classmethod
    async def create(
        cls,
        root_path: str,
        bucket_name: str,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
    ):

        client_kwargs = {
            "endpoint_url": endpoint_url,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
        }

        stack = AsyncExitStack()
        session = aioboto3.Session()

        resource = await stack.enter_async_context(
            session.resource("s3", config=Config(signature_version="s3v4"), **client_kwargs)
        )
        self = cls(resource=resource, stack=stack, root_path=root_path)
        self.bucket = await self.ensure_bucket(bucket_name)
        return self

    async def ensure_bucket(self, bucket_name) -> s3_resources.Bucket:
        try:
            await self.resource.meta.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            await self.resource.meta.client.create_bucket(Bucket=bucket_name)

        bucket = await self.resource.Bucket(bucket_name)
        return bucket

    async def close(self):
        await self.stack.aclose()

    def get_full_path(self, relative_key):
        logging.debug(f"client root_path={self.root_path}")
        return str(Path(self.root_path).joinpath(relative_key))

    async def write_object(
        self,
        relative_key: str,
        temp_object_path: str,
        content_type: str | None = "application/pdf",  # TODO rxnormlinker
    ):
        await self.bucket.upload_file(
            Filename=temp_object_path,
            Key=self.get_full_path(relative_key),
            ExtraArgs={"ContentType": content_type},
        )

    async def write_object_mem(self, relative_key: str, object: bytes | str) -> None:
        key = self.get_full_path(relative_key)
        await self.bucket.put_object(Key=key, Body=object)
        return f"{self.bucket.name}/{key}"

    async def download_directory(self, relative_prefix, local_path):
        prefix = self.get_full_path(relative_prefix)
        nopref_prefix = prefix.removeprefix("/")
        obj: s3_resources.Object
        async for obj in self.bucket.objects.filter(Prefix=prefix):
            nopref_key = obj.key.removeprefix("/")
            rel_prefix = nopref_key.removeprefix(nopref_prefix).removeprefix("/")
            rel_path: AsyncPath = AsyncPath(local_path / rel_prefix)
            if not await rel_path.parent.exists():
                await os.makedirs(rel_path.parent)
            await self.bucket.download_file(obj.key, str(rel_path))

    async def read_object(self, relative_key: str) -> bytes:
        body = await self.read_object_stream(relative_key)
        bytes = await body.read()
        return bytes

    @asynccontextmanager
    async def read_object_to_tempfile(
        self, relative_key, suffix=None, delete=True, dir=None, prefix=None
    ):
        async with tempfile.NamedTemporaryFile(
            prefix=prefix, suffix=suffix, dir=dir, delete=delete
        ) as temp:
            doc = await self.read_object(relative_key)
            await temp.write(doc)
            yield temp.name

    async def read_object_stream(self, relative_key):
        key = self.get_full_path(relative_key)
        bucket_object: s3_resources.Object = await self.bucket.Object(key)
        #  TODO turtles all the way down
        object = await bucket_object.get()
        return object["Body"]

    async def read_utf8_object(self, relative_key: str):
        object = await self.read_object(relative_key)
        return object.decode("utf-8")

    async def object_exists(self, relative_key):
        try:
            key = self.get_full_path(relative_key)
            await self.resource.meta.client.head_object(Bucket=self.bucket.name, Key=key)
            return True
        except ClientError:
            return False

    def get_signed_url(self, relative_key, expires_in_seconds=60):
        key = self.get_full_path(relative_key)
        return self.resource.meta.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket.name,
                "Key": key,
            },
            ExpiresIn=expires_in_seconds,
        )

    def get_signed_upload_url(self, relative_key, expires_in_seconds=60):
        key = self.get_full_path(relative_key)
        return self.resource.meta.client.generate_presigned_post(
            self.bucket.name,
            key,
            ExpiresIn=expires_in_seconds,
        )
