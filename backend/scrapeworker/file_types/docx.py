import docx2txt


def docx_to_text(temp_path: str):
    text = docx2txt.process(temp_path)
    return text


async def parse_metadata(temp_path, url) -> dict[str, str]:
    pass
