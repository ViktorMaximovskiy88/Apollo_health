from jarowinkler import jarowinkler_similarity

from backend.common.models.lineage import DocumentAnalysis
from backend.scrapeworker.common.utils import jaccard


class LineageMatcher:
    def __init__(self, doc_a: DocumentAnalysis, doc_b: DocumentAnalysis):
        #  text similarity
        self.doc_a = doc_a
        self.doc_b = doc_b
        self.element_text_match = jarowinkler_similarity(doc_a.element_text, doc_b.element_text)
        self.parent_text_match = jarowinkler_similarity(doc_a.parent_text, doc_b.parent_text)
        self.siblings_text_match = jarowinkler_similarity(doc_a.siblings_text, doc_b.siblings_text)

        # raw url matches
        self.filename_match = jaccard(doc_a.filename_tokens, doc_b.filename_tokens)
        self.pathname_match = jaccard(doc_a.pathname_tokens, doc_b.pathname_tokens)

        # url matches minus trusted identified attrs
        # TODO move ... dedupe
        trusted_filename_tokens_a = list(
            set(doc_a.filename_tokens) ^ set({doc_a.filename.month_abbr, doc_a.filename.year_part})
        )
        trusted_filename_tokens_b = list(
            set(doc_b.filename_tokens) ^ set({doc_b.filename.month_abbr, doc_b.filename.year_part})
        )

        self.trusted_filename_match = jaccard(trusted_filename_tokens_a, trusted_filename_tokens_b)

        self.filename_match = jaccard(doc_a.filename_tokens, doc_b.filename_tokens)
        self.pathname_match = jaccard(doc_a.pathname_tokens, doc_b.pathname_tokens)

        self.ref_indication_match = jaccard(doc_a.ref_indication_tags, doc_b.ref_indication_tags)
        self.focus_indication_match = jaccard(
            doc_a.focus_indication_tags, doc_b.focus_indication_tags
        )

        self.ref_therapy_match = jaccard(doc_a.ref_therapy_tags, doc_b.ref_therapy_tags)
        self.focus_therapy_match = jaccard(doc_a.focus_therapy_tags, doc_b.focus_therapy_tags)

    def exec(self) -> bool:
        rule_sets = ["revised_document", "updated_document"]
        match = False

        for rule_set in rule_sets:
            rule = getattr(self, rule_set)
            match = rule()
            if match:
                print(f"matched rule '{rule_set}'")
                break

        return match

    ###
    # Rule sets: have precedence and are composed of rules (tbd refactor)
    ###
    # same base url, same url, same doc, new doc revision/updated
    def revised_document(self):
        return (
            # url exact match
            self.filename_match == 1
            and self.pathname_match == 1
            # focus exact match
            and self.focus_therapy_match == 1
            and self.focus_indication_match == 1
        )

    # same base url, update date parts in url, new version/publish
    def updated_document(self):
        return (
            self.filename_match >= 0.60 or self.element_text_match >= 0.90
        ) and self.ref_indication_match >= 0.85

    ###
    #  Scored rules
    ###
    def trusted_state_match(self):
        return True

    def maybe_state_match(self):
        return True
