import asyncio

from backend.common.storage.client import DiffStorageClient, TextStorageClient
from backend.common.storage.hash import hash_full_text


class TextHandler:
    def __init__(self) -> None:
        self.text_client = TextStorageClient()
        self.diff_client = DiffStorageClient()

    async def save_text(self, text: str, ext="txt") -> str:
        hash = hash_full_text(text)
        dest_path = f"{hash}.{ext}"
        if self.text_client.object_exists(dest_path):
            return hash
        bytes_obj = bytes(text, "utf-8")
        self.text_client.write_object_mem(dest_path, bytes_obj)
        return hash

    def save_diff(self, diff: str | bytes, a_name: str, b_name: str) -> str:
        diff_name = f"{a_name}-{b_name}"
        dest_path = f"{diff_name}.diff"
        self.diff_client.write_object_mem(dest_path, diff)
        return diff_name

    async def create_diff(self, a_name: str, b_name: str) -> tuple[str, bytes]:
        diff_name = f"{a_name}-{b_name}"
        dest_path = f"{diff_name}.diff"
        if self.diff_client.object_exists(dest_path):
            diff = self.diff_client.read_object(dest_path)
            return diff_name, diff

        a_path = f"{a_name}.txt"
        b_path = f"{b_name}.txt"
        with self.text_client.read_object_to_tempfile(
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
            diff_name = self.save_diff(diff_out, a_name, b_name)
            return diff_name, diff_out
