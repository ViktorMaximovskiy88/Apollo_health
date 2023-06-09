import asyncio
import html
import os
import zipfile
from datetime import datetime, timedelta
from logging import Logger
from typing import Any, Coroutine, Hashable

import pandas as pd
from pandas import DataFrame
from playwright.async_api import ProxySettings

from backend.common.core.enums import CmsDocType
from backend.common.models.proxy import Proxy
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_full_text
from backend.common.storage.s3_client import AsyncS3Client
from backend.scrapeworker.common.aio_downloader import AioDownloader
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.cms.cms_doc import CmsDoc
from backend.scrapeworker.scrapers.cms.helpers import (
    get_data_source_item,
    group_table_by,
    search_data_frame,
    to_date_string,
)


class CMSDownloader:
    cms_cache: dict[CmsDocType, "CMSDownloader"] = {}
    cms_cache_times: dict[CmsDocType, datetime] = {}

    def __init__(
        self,
        downloader: AioDownloader,
        cms_doc: CmsDoc,
        proxies: list[tuple[Proxy | None, ProxySettings | None]],
    ) -> None:
        self.downloading = False
        self.data_source = None
        self.downloader = downloader
        self.cms_doc = cms_doc
        self.proxies = proxies

    @classmethod
    def from_cache(
        cls,
        cms_doc: CmsDoc,
        downloader: AioDownloader,
        proxies: list[tuple[Proxy | None, ProxySettings | None]],
    ):
        now = datetime.now()

        cms_downloader = cls.cms_cache.get(cms_doc.type)
        time_diff = now - cls.cms_cache_times.get(cms_doc.type, now)
        if not cms_downloader or time_diff > timedelta(hours=1):
            cms_downloader = cls(downloader, cms_doc, proxies)
            print(f"Creating new CMSDownloader for {cms_doc.type}")
            cls.cms_cache[cms_doc.type] = cms_downloader
            cls.cms_cache_times[cms_doc.type] = now

        return cms_downloader

    def _parse_documents_data(self, temp_path: str) -> list[dict[str, str | DataFrame]]:
        """
        Convert downloaded dataset (CSV) to pandas data frames
        """
        data_source: list[dict[str, str | DataFrame]] = []
        all_csv = [file for file in os.listdir(temp_path) if file.endswith(".csv")]
        for csv in all_csv:
            data_source.append(
                {
                    "file": csv.split(".")[0],
                    "content": pd.read_csv(f"{temp_path}/{csv}", encoding="ISO-8859-1"),
                }
            )
        return data_source

    def _get_data_source_item(self, name: str, data_source) -> DataFrame | None:
        """
        Retrieve a DataFrame by csv file name.
        :param name: csv file name (without extension)
        :return: Target DataFrame
        """
        found_items = [item for item in data_source if item["file"] == name]
        if len(found_items) > 0:
            return found_items[0]["content"]
        else:
            return None

    async def download_and_parse(self):
        while self.downloading:
            await asyncio.sleep(1)

        if self.data_source is not None:
            return self.data_source

        self.downloading = True
        download_url = self.cms_doc.download_url()
        if not download_url:
            self.downloading = True
            return []
        download = DownloadContext(
            request=Request(url=download_url), metadata=Metadata(base_url=download_url)
        )
        local_path = self.cms_doc.local_path()
        async with self.downloader.try_download_to_tempfile(download, self.proxies) as (
            temp_path,
            _checksum,
        ):
            if not temp_path:
                self.downloading = True
                return []
            # unzip the zip and the csv zip inside
            with zipfile.ZipFile(temp_path, "r") as zip_ref:
                zip_ref.extractall(local_path)
            with zipfile.ZipFile(
                f"{local_path}/{self.cms_doc.inner_archive_name()}", "r"
            ) as zip_ref:
                zip_ref.extractall(local_path)
            data_source = self._parse_documents_data(local_path)
        self.data_source = data_source
        self.downloading = False
        return data_source

    async def download_and_get_values(self, source: str) -> DataFrame | None:
        data_source = await self.download_and_parse()
        return self._get_data_source_item(source, data_source)


class CMSScraper:
    def __init__(
        self,
        cms_doc: CmsDoc,
        target_ids: list[int],
        downloader: AioDownloader,
        doc_client: DocumentStorageClient | AsyncS3Client,
        proxies: list[tuple[Proxy | None, ProxySettings | None]],
        log: Logger,
    ) -> None:
        self.cms_doc = cms_doc
        self.downloader = downloader
        self.doc_client = doc_client
        self.proxies = proxies
        self.target_ids = target_ids
        self.data_source: list[dict[str, str | DataFrame]] = []
        self.log = log

    async def _set_data_source(self, overwrite: bool = False):
        if self.data_source and not overwrite:
            return
        self.data_source = await CMSDownloader.from_cache(
            self.cms_doc, self.downloader, self.proxies
        ).download_and_parse()

    def _get_data_source_item(self, name: str) -> DataFrame | None:
        """
        Retrieve a DataFrame by csv file name.
        :param name: csv file name (without extension)
        :return: Target DataFrame
        """
        found_items = [item for item in self.data_source if item["file"] == name]
        if len(found_items) > 0:
            return found_items[0]["content"]  # type: ignore
        return None

    def _extract_data_for_table(self, field, row_id) -> str:
        """
        Retrieve data from data source for specific row of table
        :param field: field name
        :param row_id: row content
        :return: HTML string
        """
        table_template = ""
        parent_identifier = None
        identifiers = [list(identifier.keys())[0] for identifier in row_id]
        values = [list(identifier.values())[0] for identifier in row_id]
        if "delimiter" in field:
            table_template = table_template + field["delimiter"]
        if "parent_source" in field:
            parent_source = self._get_data_source_item(field["parent_source"])
            if parent_source is not None:
                search_result: list[dict[Hashable, Any]] = search_data_frame(
                    parent_source, identifiers, values, self.log
                )  # type: ignore
                parent_identifier = [result[field["parent_identifier"]] for result in search_result]
        ds = self._get_data_source_item(field["source"])
        if ds is None:
            return table_template
        if parent_identifier is not None:
            search_result = search_data_frame(
                ds, [field["identifier"]], parent_identifier, self.log, operator="|"
            )  # type: ignore
            table_template += "<br/>".join(
                [str(search_item[field["field"]]) for search_item in search_result]
            )
        else:
            search_result = search_data_frame(ds, identifiers, values, self.log)  # type: ignore
            table_template += str(search_result[0][field["field"]])
            if "min_length" in field and len(table_template) < field["min_length"]:
                return f"0{table_template}"
        return table_template

    def _build_group(
        self,
        available_groups: list[dict[Hashable, Any]],
        data_set_identifiers: list[str],
        mapping_item: dict[str, Any],
        url_identifiers: list[int],
    ) -> str:
        """
        Generate a group field for group mapping element
        :param data_set_identifiers: document identifiers from target dataset
        :param mapping_item: current mapping item data
        :param url_identifiers: document identifiers from target URL
        :return: HTML string
        """

        all_groups = list(set([group[mapping_item["group_field"]] for group in available_groups]))
        groups_html_template = ""
        for group_id in all_groups:
            for mapping_group in mapping_item["groups"]:
                if mapping_group["type"] == "text":
                    groups_html_template += (
                        f'<p><strong>Group {group_id} {mapping_group["name"]}:</strong>'
                    )
                    group_data_source = self._get_data_source_item(mapping_group["source"])
                    if group_data_source is None:
                        continue
                    group_source: list[dict[Hashable, Any]] = search_data_frame(
                        group_data_source, data_set_identifiers, url_identifiers, self.log
                    )  # type: ignore
                    group_item = [
                        item
                        for item in group_source
                        if item[mapping_item["group_field"]] == group_id
                    ]
                    field_item = group_item[0][mapping_group["field"]]
                    if field_item != field_item:
                        field_item = "N/A"
                    groups_html_template += field_item + "</p>"

                if mapping_group["type"] == "single_table":
                    groups_html_template += (
                        f'<p><strong>Group {group_id} {mapping_group["name"]}:</strong></p>'
                    )
                    group_data_source = self._get_data_source_item(mapping_group["source"])
                    if group_data_source is None:
                        continue
                    group_source: list[dict[Hashable, Any]] = search_data_frame(
                        group_data_source, data_set_identifiers, url_identifiers, self.log
                    )  # type: ignore
                    table_item_rows = [
                        item
                        for item in group_source
                        if item[mapping_item["group_field"]] == group_id
                    ]

                    groups_html_table_template = ""
                    if len(table_item_rows) > 0:
                        groups_html_table_template += "<table><thead><tr>"
                        for table_field in mapping_group["fields"]:
                            groups_html_table_template += f'<th>{table_field["name"]}</th>'
                        groups_html_table_template += "</tr></thead><tbody>"
                        for table_item_row in table_item_rows:
                            groups_html_table_template += "<tr>"
                            for table_field in mapping_group["fields"]:
                                if (
                                    table_item_row[table_field["field"]]
                                    != table_item_row[table_field["field"]]
                                ):
                                    return groups_html_template + "N/A"
                                groups_html_table_template += (
                                    f'<td>{table_item_row[table_field["field"]]}</td>'
                                )
                            groups_html_table_template += "</tr>"
                        groups_html_table_template += "</tbody></table>"
                        groups_html_template += groups_html_table_template
                    else:
                        groups_html_template += "N/A"
        return groups_html_template

    def _build_text(
        self,
        data_set_identifiers: list,
        mapping_item: dict,
        mapping_item_type: str,
        url_identifiers,
    ) -> str:
        """
        Generate a text field string for text or date mapping element
        :param data_set_identifiers: document identifiers from target dataset
        :param mapping_item: current mapping item data
        :param mapping_item_type: mapping item type: text or date
        :param url_identifiers: document identifiers from target URL
        :return: HTML string
        """
        data_source_item = self._get_data_source_item(mapping_item["source"])
        if data_source_item is None:
            return "N/A"
        data_source_row: list[dict[Hashable, Any]] = search_data_frame(
            data_source_item, data_set_identifiers, url_identifiers, self.log
        )  # type: ignore
        if "class" in mapping_item:
            if len(data_source_row) == 0:
                return ""
            item = str(data_source_row[0][mapping_item["field"]])
            render_div = f'<div class="row"><div class="{mapping_item["class"]}">{item}</div></div>'
            return render_div
        if len(data_source_row) == 0:
            return "N/A"
        if "transform" in mapping_item:
            transformation = mapping_item["transform"]
            transformation_data_source = self._get_data_source_item(transformation["source"])
            if transformation_data_source is None:
                return "N/A"
            rows = [row[mapping_item["field"]] for row in data_source_row]
            fields = [mapping_item["field"] for __ in rows]
            if "identifier" in transformation:
                fields = [transformation["identifier"]]
            result: list[dict[Hashable, Any]] = search_data_frame(
                transformation_data_source, fields, rows, self.log, operator="|"
            )  # type: ignore
            if len(result) == 0:
                return "N/A"
            results = [res[transformation["field"]] for res in result]
            return "<br/>".join(results)
        if "source_field" in mapping_item:
            replace_item = str(data_source_row[0][mapping_item["source_field"]])
        else:
            replace_item = str(data_source_row[0][mapping_item["field"]])
        if replace_item == "nan":
            replace_item = "N/A"
        if mapping_item_type == "date" and replace_item != "N/A":
            replace_item = to_date_string(replace_item)
        if "split_by" in mapping_item:
            if mapping_item["split_by"] not in replace_item:
                return replace_item
            split_items = [
                split_item
                for split_item in replace_item.split(mapping_item["split_by"])
                if split_item != ""
            ]
            replace_item = "<ul>"
            for item in split_items:
                replace_item += f"<li>{item}</li>"
            replace_item += "</ul>"
        if "prefix" in mapping_item:
            replace_item = f'{mapping_item["prefix"]}{replace_item}'
        return replace_item

    async def _build_list(self, data_set_identifiers, mapping_item, url_identifiers) -> str:
        """
        Generate HTML <UL> list for list mapping type
        :param data_set_identifiers: document identifiers from target dataset
        :param mapping_item: current mapping item data
        :param url_identifiers: document identifiers from target URL
        :return: HTML string
        """
        list_template = """
        <ul style="list-style-type:none;">
        """
        for item in mapping_item["items"]:
            list_template += f'<li><strong>{item["name"]}</strong><br/>'
            data_source = self._get_data_source_item(item["source"])
            if data_source is None:
                continue
            rows: list[dict[Hashable, Any]] = search_data_frame(
                data_source, data_set_identifiers, url_identifiers, self.log
            )  # type: ignore
            for field in item["fields"]:
                if "static" in field:
                    list_template += f'<br/>{field["static"]}'
                    continue
                results = [row for row in rows if row[field["column"]] == row[field["column"]]]
                if "condition" in field:
                    condition = field["condition"]
                    results = [
                        result
                        for result in results
                        if result[condition["field"]] == condition["equals"]
                    ]
                if "transform" in field:
                    results = [int(result[field["column"]]) for result in results]
                else:
                    results = [result[field["column"]] for result in results]
                if len(results) > 0:
                    if "transform" in field:
                        if "shared_source" in field["transform"]:
                            transform_item = field["transform"]
                            shared_doc = CmsDoc(CmsDocType(transform_item["shared_source"]))
                            cms_downloader = CMSDownloader.from_cache(
                                shared_doc, self.downloader, self.proxies
                            )
                            target_data_frame = await cms_downloader.download_and_get_values(
                                transform_item["source"]
                            )
                            if target_data_frame is None:
                                transform_results = []
                            else:
                                transform_results = search_data_frame(
                                    target_data_frame,
                                    [transform_item["identifier"]],
                                    results,
                                    self.log,
                                    operator="|",
                                )  # type: ignore
                        else:
                            transform_data_source = self._get_data_source_item(
                                field["transform"]["source"]
                            )
                            if transform_data_source is None:
                                transform_results = []
                            else:
                                transform_results: list[dict[Hashable, Any]] = search_data_frame(
                                    transform_data_source,
                                    [field["transform"]["identifier"]],
                                    results,
                                    self.log,
                                    operator="|",
                                )  # type: ignore
                        if len(transform_results) > 0:
                            list_template += f'{field["display_name"]}<br/>'
                            transformed_fields = []
                            for trans_result in transform_results:
                                new_item = []
                                for trans_field in field["transform"]["fields"]:
                                    new_item.append(str(trans_result[trans_field]))
                                transformed_fields.append(" - ".join(new_item))

                            list_template += "<br/>".join(transformed_fields)
                            list_template += "<br/>"
                        else:
                            list_template += "N/A"
                    else:
                        if "display_name" in field:
                            list_template += f'{field["display_name"]}<br/>'
                        list_template += "<br/>".join([str(identifier) for identifier in results])
                elif "display_name" not in item["fields"][0]:
                    list_template += "N/A"
            list_template += "</li>"
        list_template += "</ul>"
        return list_template

    def _build_single_table(self, data_set_identifiers, mapping_item, url_identifiers) -> str:
        """
        Generate HTML table list for single_table mapping type
        :param data_set_identifiers: document identifiers from target dataset
        :param mapping_item: current mapping item data
        :param url_identifiers: document identifiers from target URL
        :return: HTML string
        """
        table_template = """
        <table>
            <thead>
                <tr>
        """
        for field in mapping_item["fields"]:
            table_template += f'<th>{html.escape(field["name"])}</th>'
        table_template += "</tr></thead><tbody>"
        target_table = mapping_item["rows_source"]["table"]
        data_source_item = self._get_data_source_item(target_table)
        if "exclude" in mapping_item["rows_source"]:
            index = data_set_identifiers.index(mapping_item["rows_source"]["exclude"])
            del data_set_identifiers[index]
            del url_identifiers[index]
        if data_source_item is None:
            return table_template
        rows: list[dict[Hashable, Any]] = search_data_frame(
            data_source_item, data_set_identifiers, url_identifiers, self.log
        )  # type: ignore
        if len(rows) == 0:
            return "N/A"
        if "order_by_desc" in mapping_item:
            rows.sort(key=lambda x: x[mapping_item["order_by_desc"]], reverse=True)
        if "order_by_asc" in mapping_item:
            rows.sort(key=lambda x: x[mapping_item["order_by_asc"]])

        for row in rows:
            table_template += "<tr>"
            for field in mapping_item["fields"]:
                table_template += "<td>"
                field_item = row[field["field"]]
                if "prefix" in field:
                    table_template += html.escape(field["prefix"])
                if "format" in field:
                    if field["format"]:
                        field_item = to_date_string(str(field_item))
                table_template += html.escape(str(field_item))
                table_template += "</td>"
            table_template += "</tr>"
        table_template += "</tbody></table>"
        # parse html table and group rows by code
        if "group_by" in mapping_item:
            table_template = group_table_by(table_template)
        return table_template

    def _build_table(
        self, data_set_identifiers: list, mapping_item: dict, url_identifiers: list[int]
    ) -> str:
        """
        Generate a HTML string for table mapping element
        :param data_set_identifiers: document identifiers from target dataset
        :param mapping_item: current mapping item data
        :param url_identifiers: document identifiers from target URL
        :return: HTML string
        """
        target_table = mapping_item["rows_source"]["table"]
        target_columns = mapping_item["rows_source"]["columns"]
        data_source_item = self._get_data_source_item(target_table)
        if data_source_item is None:
            return "N/A"
        target_data_source: list[dict[Hashable, Any]] = search_data_frame(
            data_source_item, data_set_identifiers, url_identifiers, self.log
        )  # type: ignore
        row_id_set = []
        for ds in target_data_source:
            cols = []
            for column in target_columns:
                cols.append({column: ds[column]})
            row_id_set.append(cols)
        table_template = []
        for row_id in row_id_set:
            table_template_item = {}
            for field in mapping_item["fields"]:
                table_template_item[field["name"]] = self._extract_data_for_table(field, row_id)
                if "append" in field:
                    table_template_item[field["name"]] += self._extract_data_for_table(
                        field["append"], row_id
                    )
            table_template.append(table_template_item)
        if "order_by" in mapping_item:
            table_template.sort(key=lambda x: x[mapping_item["order_by"]])
        html_table_template = ""
        for row in table_template:
            html_table_template += "<tr>"
            for value in row.values():
                html_table_template += f"<td>{value}</td>"
            html_table_template += "<t/r>"
        return html_table_template

    async def _save_html(self, html: str) -> str:
        checksum = hash_full_text(html)
        dest_path = f"{checksum}.html"
        exists = self.doc_client.object_exists(dest_path)
        if isinstance(exists, Coroutine):
            exists = await exists
        if not exists:
            bytes_obj = bytes(html, "utf-8")
            write = self.doc_client.write_object_mem(dest_path, bytes_obj)
            if isinstance(write, Coroutine):
                await write
        return checksum

    async def scrape_and_create(self, downloads: list[DownloadContext]) -> None:
        """
        fetch url and try to download the zip file response
        unzip the zip and the csv zip inside
        Get the relevant "mappings"
        for each mapping, run html construct code
        convert html to pdf
        queue pdf as download
        """
        await self._set_data_source()
        html_template = self.cms_doc.html_template()
        mapping = self.cms_doc.document_mapping()
        data_set_identifiers: list[str] = mapping["data_set_identifiers"]

        mapping_item: dict[str, Any]
        for mapping_item in mapping["mapping"]:
            mapping_item_type = mapping_item["type"]
            if mapping_item_type == "group":
                data_source_item = self._get_data_source_item(mapping_item["source"])
                if data_source_item is None:
                    continue
                available_groups: list[dict[Hashable, Any]] = search_data_frame(
                    data_source_item, data_set_identifiers, self.target_ids, self.log
                )  # type: ignore
                if len(available_groups) == 0:
                    html_template = html_template.replace(f'${mapping_item["field"]}', "N/A")
                    continue
                groups_html_template = self._build_group(
                    available_groups, data_set_identifiers, mapping_item, self.target_ids
                )
                html_template = html_template.replace(
                    f'${mapping_item["field"]}', groups_html_template
                )

            if mapping_item_type == "text" or mapping_item_type == "date":
                replace_item = self._build_text(
                    data_set_identifiers, mapping_item, mapping_item_type, self.target_ids
                )

                html_template = html_template.replace(f'${mapping_item["field"]}', replace_item)

            if mapping_item_type == "single_table":
                table_template = self._build_single_table(
                    data_set_identifiers, mapping_item, self.target_ids
                )
                html_template = html_template.replace(f'${mapping_item["field"]}', table_template)

            if mapping_item_type == "list":
                table_template = await self._build_list(
                    data_set_identifiers, mapping_item, self.target_ids
                )
                html_template = html_template.replace(f'${mapping_item["field"]}', table_template)

            if mapping_item_type == "table":
                table_template = self._build_table(
                    data_set_identifiers, mapping_item, self.target_ids
                )
                html_template = html_template.replace(f'${mapping_item["field"]}', table_template)
        checksum = await self._save_html(html_template)
        downloads.append(
            DownloadContext(
                direct_scrape=True,
                file_extension="html",
                file_hash=checksum,
                file_name=self.cms_doc.download_url(),
                metadata=Metadata(base_url=self.cms_doc.download_url()),
                request=Request(
                    url=self.cms_doc.download_url(), filename=self.cms_doc.download_url()
                ),
            )
        )


class CMSScrapeController:
    def __init__(
        self,
        doc_types: list[CmsDocType],
        downloader: AioDownloader,
        doc_client: DocumentStorageClient | AsyncS3Client,
        proxies: list[tuple[Proxy | None, ProxySettings | None]],
        log: Logger,
    ) -> None:
        self.doc_types = doc_types
        self.downloader = downloader
        self.doc_client = doc_client
        self.proxies = proxies
        self.scraper_queue: list[CMSScraper] = []
        self.log = log

    async def get_data_ids(self, doc: CmsDoc) -> list[list[int]]:
        downloader = CMSDownloader.from_cache(
            downloader=self.downloader, cms_doc=doc, proxies=self.proxies
        )
        data_source = await downloader.download_and_parse()
        mapping = doc.document_mapping()
        # Get file containing complete list of identifiers
        data_source = get_data_source_item(mapping["core_file"], data_source)
        if data_source is None:
            return []

        [column_id_1, column_id_2] = mapping["data_set_identifiers"]
        id_list_1: list[str] = data_source[column_id_1].to_list()
        id_list_2: list[str] = data_source[column_id_2].to_list()

        # each nested list is one pair of identifiers, or one document to create
        final_ids: list[list[int]] = []
        for i, id in enumerate(id_list_1):
            id_2 = id_list_2[i]
            id_pair = [int(id), int(id_2)]
            final_ids.append(id_pair)

        return final_ids

    async def create_all_scrapers(self):
        for doc_type in self.doc_types:
            doc = CmsDoc(doc_type)
            target_identifiers = await self.get_data_ids(doc)
            for id_pair in target_identifiers:
                scraper = CMSScraper(
                    cms_doc=doc,
                    target_ids=id_pair,
                    downloader=self.downloader,
                    doc_client=self.doc_client,
                    proxies=self.proxies,
                    log=self.log,
                )
                self.scraper_queue.append(scraper)

    async def execute(self):
        await self.create_all_scrapers()
        downloads = []
        scrapes = [scraper.scrape_and_create(downloads) for scraper in self.scraper_queue]
        await asyncio.gather(*scrapes)
        return downloads

    async def batch_execute(self, batch_size: int = 20):
        await self.create_all_scrapers()
        while self.scraper_queue:
            current_scrapers = self.scraper_queue[:batch_size]
            downloads: list[DownloadContext] = []
            scrapes = [scraper.scrape_and_create(downloads) for scraper in current_scrapers]
            await asyncio.gather(*scrapes)
            yield downloads
            self.scraper_queue = self.scraper_queue[batch_size:]
