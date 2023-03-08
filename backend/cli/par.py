import logging
import sys
from pathlib import Path

import asyncclick as click
import pandas as pd

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from pymongo import InsertOne, UpdateOne

from backend.common.db.init import aws_get_motor, aws_init_db, init_db
from backend.common.models.doc_document import DocDocument, PydanticObjectId
from backend.common.models.search_codes import SearchableType, SearchCodeSet
from backend.common.models.site import ScrapeMethodConfiguration, Site
from backend.common.models.user import User
from backend.scrapeworker.common.utils import find
from backend.scrapeworker.doc_type_matcher import DocTypeMatcher

log = logging.getLogger(__name__)

aws_mongo = None
# aws_mongo = {
#     "host": "apollo-dev-use1-mmit-01.3qm7h.mongodb.net",
#     "database": "source-hub",
#     "user": "access_key",
#     "password": "secret_key",
#     "session": "session_id",
# }


@click.group()
@click.pass_context
@click.option("--file", help="File to parse", required=True, type=str)
async def par(ctx, file: str):
    if aws_mongo:
        client, database = aws_get_motor(**aws_mongo)
        await aws_init_db(database=database)
    else:
        await init_db()


@par.command()
@click.pass_context
async def prev_par_ids(ctx):
    file = ctx.parent.params["file"]
    parsed_path = Path(file)
    output_file = parsed_path.parent / f"{parsed_path.stem}-proposed.csv"
    df = pd.read_csv(file, skipinitialspace=True)
    df["EffectiveDate"] = pd.to_datetime(df["EffectiveDate"])

    batch = []
    for index, row in df.iterrows():
        docs = (
            await DocDocument.find_many({"locations.url": row["DocumentUrl"]})
            .sort("-final_effective_date")
            .to_list()
        )

        if len(docs) >= 1:
            print(index)
            doc = docs[0]
            df.loc[index, "SH_EffectiveDate"] = doc.final_effective_date
            df.loc[index, "DateMatch"] = (
                "SH_GTE_PAR" if doc.final_effective_date >= row["EffectiveDate"] else "SH_LT_PAR"
            )
            df.loc[index, "SH_Checksum"] = doc.checksum
            df.loc[index, "SH_DocDocId"] = doc.id
            df.loc[index, "ChecksumMatch"] = (
                "Lastest" if row["Checksum"].lower() != doc.checksum else "Same"
            )

            if (
                doc.final_effective_date >= row["EffectiveDate"]
                and row["Checksum"].lower() != doc.checksum
            ):
                batch.append(
                    UpdateOne({"_id": doc.id}, {"$set": {"previous_par_id": row["ParDocumentId"]}})
                )

    logging.info(f"items pending bulk write -> {len(batch)}")
    result = await DocDocument.get_motor_collection().bulk_write(batch)
    logging.info(
        f"bulk_write -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    df.to_csv(output_file)


@par.command()
@click.pass_context
async def doc_type_validation(ctx):
    file = ctx.parent.params["file"]
    parsed_path = Path(file)
    output_file = parsed_path.parent / f"{parsed_path.stem}-proposed.csv"

    df = pd.read_csv(file)
    df["DocDocId"] = df["Url"].str.extract(r"([a-fA-F\d]{24})", expand=False).str.strip()

    for index, row in df.iterrows():
        doc = await DocDocument.get(PydanticObjectId(row["DocDocId"]))
        if doc:
            location = doc.locations[0]
            matched = DocTypeMatcher(
                raw_text="",
                raw_link_text=location.link_text,
                raw_url=location.url,
                raw_name=doc.name,
            ).exec()
            df.loc[index, "CurrentDocType"] = doc.document_type
            if matched:
                df.loc[index, "ProposedDocType"] = matched.document_type
            df.loc[index, "LocationCount"] = len(doc.locations)
            df.loc[index, "Name"] = doc.name
            df.loc[index, "LinkText"] = location.link_text
            df.loc[index, "ExternalUrl"] = location.url

    df.insert(0, "CurrentDocType", df.pop("CurrentDocType"))
    df.insert(1, "ExpectedDocType", df.pop("ExpectedDocType"))
    df.insert(2, "ProposedDocType", df.pop("ProposedDocType"))
    df.insert(3, "Name", df.pop("Name"))
    df.insert(4, "LinkText", df.pop("LinkText"))

    df.to_csv(output_file)


@par.command()
@click.pass_context
async def tricare_token_import(ctx):
    file = ctx.parent.params["file"]
    df = pd.read_csv(file, encoding="latin1")

    app_config_settings = await SearchCodeSet.find_one({"type": SearchableType.TRICARE})
    if not app_config_settings:
        app_config_settings = SearchCodeSet(type=SearchableType.TRICARE, codes=[])

    app_config_settings.codes = df["Token"].tolist()
    await app_config_settings.save()

    log.info(f"tokens updated len={len(app_config_settings.codes)}")


@par.command()
@click.pass_context
@click.option(
    "--dry-run",
    help="Dry run option to not insert into DB",
    required=False,
    type=bool,
    is_flag=True,
    default=False,
)
async def navigator_import(ctx, dry_run: bool):
    file = ctx.parent.params["file"]
    df = pd.read_csv(file)

    user = await User.get_api_user()
    default_config = {
        "document_extensions": ["pdf"],
        "url_keywords": [],
        "proxy_exclusions": [],
        "wait_for": [],
        "wait_for_timeout_ms": 500,
        "base_url_timeout_ms": 30000,
        "search_in_frames": False,
        "follow_links": False,
        "follow_link_keywords": [],
        "follow_link_url_keywords": [],
        "searchable": False,
        "searchable_playbook": None,
        "searchable_type": [],
        "searchable_input": None,
        "searchable_submit": None,
        "attr_selectors": [],
        "html_attr_selectors": [],
        "html_exclusion_selectors": [],
        "focus_section_configs": [],
        "allow_docdoc_updates": False,
    }

    base_url = "https://client.formularynavigator.com/Search.aspx"
    sites = {}
    for _index, row in df.iterrows():
        client_name = row["NavClient Name"].strip()
        formulary_id = row["Nav Formulary ID"]
        formulary_type = row["Nav Formulary Type"].strip()
        name = f"{client_name} | {formulary_id} | {formulary_type}"
        url = f"{base_url}?siteCode={row['WebsiteID/SIteCode']}"

        if not sites.get(name, None):
            sites[name] = []

        sites[name].append(
            {"url": str(url), "name": formulary_id, "status": "ACTIVE"},
        )
    batch = []
    for name, base_urls in sites.items():
        urls = [base_url["url"] for base_url in base_urls]
        site = await Site.find_one({"base_urls.url": {"$in": urls}})

        if site:
            log.info(f"site found {site.id} name={name}, updating {len(site.base_urls)}")
            update = False
            for base_url in base_urls:
                exists = find(lambda x: x["url"] == base_url["url"], base_urls)
                if not exists:
                    update = True
                    site.base_urls.append(base_url)
                else:
                    log.info(f"base_url={base_url} already exists for id={site.id}")

            if update:
                batch.append(UpdateOne({"_id": site.id}, {"$set": {"base_urls": site.base_urls}}))
        else:
            log.info(f"site not found name={name}, creating")
            site = Site(
                name=name,
                creator_id=user.id,
                base_urls=base_urls,
                scrape_method="SimpleDocumentScrape",
                collection_method="AUTOMATED",
                scrape_method_configuration=ScrapeMethodConfiguration(**default_config),
                tags=["Formulary Navigator", "FN Client API"],
                disabled=False,
                cron="0 16 * * *",
            )

            batch.append(InsertOne(site.dict()))

    logging.info(f"items pending bulk write -> {len(batch)}")
    if not dry_run and batch:
        result = await Site.get_motor_collection().bulk_write(batch)
        logging.info(
            f"bulk_write -> acknowledged={result.acknowledged}"
            f" matched_count={result.matched_count}"
            f" inserted_count={result.inserted_count}"
            f" modified_count={result.modified_count}"
        )
