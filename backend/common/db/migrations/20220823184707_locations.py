import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def add_locations(self, session):
        pass
        # @above
        # base_url
        # url
        # link_text
        # closest_header
        # site_id
        # context_metadata
        # first_collected_date
        # last_collected_date

        # for every rt doc
        # move all above to location
        # unset site_id, url, base_url, scrape_task_id, logical_document_id, logical_document_version, context_metadata

        # site_id
        # base_url
        # url
        # link_text
        # first_collected_date
        # last_collected_date
        # for every doc_doc

        # move all above to location
        # unset site_id, url, base_url, link_text

        # recall that old rt_ids live on doc doc and site_scrape_tasks
        # query for all dupe checksums (20!)
        # loop through pick one as the winner.
        # merge the location of the other into the winner.
        # delete the loser doc doc (by related rt id) and the loser rt itself;
        # maybe remove the rt from whatever scrape task it was in? decrement it?

        # where else might doc docs or rt docs refs live?
        # remove all change logs related to the loser rt and doc docs


class Backward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def add_locations(self, session):
        pass
