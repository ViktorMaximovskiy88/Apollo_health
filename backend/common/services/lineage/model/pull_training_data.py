import os


class Lineager:
    def base(self, doc):
        return (doc.lang_code or "") + (doc.document_type or "")

    def existing_lineage(self, doc, arg: str | None = None) -> str:
        return str(doc.lineage_id)

    def link_text(self, doc, arg: str | None = None) -> str:
        return self.base(doc) + (doc.element_text or "")

    def link_text_up_to(self, doc, up_to: str) -> str:
        up_tos = up_to.split(",")
        text = doc.element_text or ""
        for up_to in up_tos:
            text = text.split(up_to)[0]
        return self.base(doc) + text

    def link_text_after_year(self, doc, arg: str | None = None) -> str:
        import re

        return self.base(doc) + re.sub(r"\d{4}", "", doc.element_text or "")

    def link_text_after(self, doc, after: str) -> str:
        afters = after.split(",")
        text = doc.element_text or ""
        for after in afters:
            text = text.removeprefix(after)
        return self.base(doc) + text

    def name_after(self, doc, after: str) -> str:
        return self.base(doc) + (doc.name or "").removeprefix(after)


class LineageDataFetcher:
    def __init__(self):
        self.lineager = Lineager()

    def prebuild_doc_analyses(self, doc_docs):
        import igraph as ig
        from beanie import PydanticObjectId

        from backend.common.models.lineage import DocumentAnalysis
        from backend.common.services.lineage.core import build_doc_analysis

        doc_lookup: dict[PydanticObjectId | None, int] = {
            doc.id: i for i, doc in enumerate(doc_docs)
        }
        prevs = []
        for doc in doc_docs:
            if doc.previous_doc_doc_id in doc_lookup:
                prevs.append((doc_lookup[doc.id], doc_lookup[doc.previous_doc_doc_id]))

        graph = ig.Graph(len(doc_docs))
        ig.Graph.add_edges(graph, prevs)

        analyses: list[DocumentAnalysis] = []
        for ids in graph.connected_components():
            lineage_id = PydanticObjectId()
            for id in ids:
                doc = doc_docs[id]
                doc_analysis = DocumentAnalysis(
                    doc_document_id=doc.id,
                    retrieved_document_id=doc.retrieved_document_id,
                    site_id=doc.site_id,
                    lineage_id=lineage_id,
                )
                analyses.append(build_doc_analysis(doc, doc_analysis))
        return analyses

    async def fetch_doc_analysis(
        self,
        output_dir,
        site_id_str: str,
        method: str,
        method_args: str | None = None,
        force: bool = False,
    ):
        output_path = f"{output_dir}/{site_id_str}.json.txt"
        if os.path.exists(output_path) and os.path.getsize(output_path) and not force:
            print(f"Output file {output_path} already exists, skipping")
            return

        from collections import defaultdict
        from pathlib import Path

        from beanie import PydanticObjectId

        from backend.common.db.init import init_db
        from backend.common.models.lineage import DocumentAnalysis
        from backend.common.services.document import get_site_docs

        await init_db()

        site_id = PydanticObjectId(site_id_str)
        doc_docs = await get_site_docs(site_id)
        docs = self.prebuild_doc_analyses(doc_docs)

        lineages: dict[str, list[DocumentAnalysis]] = defaultdict(list)
        for doc in docs:
            key_func = getattr(self.lineager, method)
            key = key_func(doc, method_args)
            lineages[key].append(doc)

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        with open(output_path, "w+") as f:
            for docs in lineages.values():
                lineage_id = PydanticObjectId()
                for doc in docs:
                    doc.lineage_id = lineage_id
                    f.write(f"{doc.json()}\n")


if __name__ == "__main__":
    import asyncclick as click

    @click.command()
    @click.option("--path", required=True)
    @click.option("--site-id", required=True)
    @click.option("--method", default="lineage")
    @click.option("--method-args")
    @click.option("--force")
    async def main(path, site_id, method, method_args, force):
        await LineageDataFetcher().fetch_doc_analysis(path, site_id, method, method_args, force)

    main(_anyio_backend="asyncio")
