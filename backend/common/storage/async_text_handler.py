import asyncio

from backend.common.storage.hash import hash_full_text
from backend.common.storage.s3_client import AsyncS3Client
from backend.common.storage.settings import settings


class AsyncTextHandler:
    def __init__(self, text_client: AsyncS3Client, diff_client: AsyncS3Client) -> None:
        self.text_client = text_client
        self.diff_client = diff_client

    @classmethod
    async def create(cls):
        text_client = AsyncS3Client.create(
            root_path=settings.text_path, bucket_name=settings.document_bucket
        )
        diff_client = AsyncS3Client.create(
            root_path=settings.diff_path, bucket_name=settings.document_bucket
        )
        self = cls(text_client=text_client, diff_client=diff_client)
        return self

    async def close(self):
        if self.text_client:
            self.text_client.close()
        if self.diff_client:
            self.diff_client.close()

    async def save_text(self, text: str) -> str:
        hash = hash_full_text(text)
        dest_path = f"{hash}.txt"
        if await self.text_client.object_exists(dest_path):
            return hash
        bytes_obj = bytes(text, "utf-8")
        await self.text_client.write_object_mem(dest_path, bytes_obj)
        return hash

    async def save_diff(self, diff: str | bytes, a_name: str, b_name: str) -> str:
        diff_name = f"{a_name}-{b_name}"
        dest_path = f"{diff_name}.diff"
        await self.diff_client.write_object_mem(dest_path, diff)
        return diff_name

    async def create_diff(self, a_name: str, b_name: str) -> tuple[str, bytes]:
        diff_name = f"{a_name}-{b_name}"
        dest_path = f"{diff_name}.diff"
        if await self.diff_client.object_exists(dest_path):
            diff = await self.diff_client.read_object(dest_path)
            return diff_name, diff

        a_path = f"{a_name}.txt"
        b_path = f"{b_name}.txt"
        async with self.text_client.read_object_to_tempfile(
            a_path
        ) as a_file, self.text_client.read_object_to_tempfile(b_path) as b_file:
            process = await asyncio.create_subprocess_exec(
                "git",
                "diff",
                "-U1",
                a_file,
                b_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            diff_out, _ = await process.communicate()
            diff_name = await self.save_diff(diff_out, a_name, b_name)
            return diff_name, diff_out
