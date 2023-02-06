import logging

from backend.common.tasks.processors.rescrape_doc import RescrapeDocProcessor

__all__ = ["content", "date", "doc_type", "lineage", "pdf_diff", "tag", "doc"]

from backend.common.models.tasks import TaskLog
from backend.common.tasks.processors.content import ContentTaskProcessor
from backend.common.tasks.processors.date import DateTaskProcessor
from backend.common.tasks.processors.doc_type import DocTypeTaskProcessor
from backend.common.tasks.processors.pdf_diff import PDFDiffTaskProcessor
from backend.common.tasks.processors.tag import TagTaskProcessor


def task_processor_factory(task: TaskLog):
    task_type = task.task_type
    if task_type == "PDFDiffTask":
        Processor = PDFDiffTaskProcessor
    elif task_type == "ContentTask":
        Processor = ContentTaskProcessor
    elif task_type == "DateTask":
        Processor = DateTaskProcessor
    elif task_type == "TagTask":
        Processor = TagTaskProcessor
    elif task_type == "DocTypeTask":
        Processor = DocTypeTaskProcessor
    elif task_type == "RescrapeDocTask":
        Processor = RescrapeDocProcessor
    else:
        return None

    return Processor(logger=logging)
