import logging

from jarowinkler import jarowinkler_similarity
from scipy import spatial

from backend.common.models.lineage import DocumentAnalysis
from backend.scrapeworker.common.utils import jaccard


class LineageMatcher:
    def __init__(self, doc_a: DocumentAnalysis, doc_b: DocumentAnalysis, logger=logging):
        self.logger = logger
        #  text similarity
        self.doc_a = doc_a
        self.doc_b = doc_b

        self.element_text_match = jarowinkler_similarity(doc_a.element_text, doc_b.element_text)
        self.logger.debug(f"element_text_match={self.element_text_match}")

        self.parent_text_match = jarowinkler_similarity(doc_a.parent_text, doc_b.parent_text)
        self.logger.debug(f"parent_text_match={self.parent_text_match}")

        self.siblings_text_match = jarowinkler_similarity(doc_a.siblings_text, doc_b.siblings_text)
        self.logger.debug(f"siblings_text_match={self.siblings_text_match}")

        # raw url matches
        self.filename_match = jaccard(doc_a.filename_tokens, doc_b.filename_tokens)
        self.pathname_match = jaccard(doc_a.pathname_tokens, doc_b.pathname_tokens)

        self.filename_match = jaccard(doc_a.filename_tokens, doc_b.filename_tokens)
        self.logger.debug(f"filename_match={self.filename_match}")

        self.pathname_match = jaccard(doc_a.pathname_tokens, doc_b.pathname_tokens)
        self.logger.debug(f"pathname_match={self.pathname_match}")

        self.ref_indication_match = jaccard(doc_a.ref_indication_tags, doc_b.ref_indication_tags)
        self.focus_indication_match = jaccard(
            doc_a.focus_indication_tags, doc_b.focus_indication_tags
        )

        self.ref_therapy_match = jaccard(doc_a.ref_therapy_tags, doc_b.ref_therapy_tags)
        self.logger.debug(f"ref_therapy_match={self.ref_therapy_match}")

        self.focus_therapy_match = jaccard(doc_a.focus_therapy_tags, doc_b.focus_therapy_tags)
        self.logger.debug(f"focus_therapy_match={self.focus_therapy_match}")

        self.cosine_similarity = 1 - spatial.distance.cosine(
            self.doc_a.doc_vectors[0],
            self.doc_b.doc_vectors[0],
        )
        print(f"self.cosine_similarity={self.cosine_similarity}")

        self.euclidean_distance = spatial.distance.euclidean(
            self.doc_a.doc_vectors[0],
            self.doc_b.doc_vectors[0],
        )

        print(f"self.euclidean_distance={self.euclidean_distance}")

    def exec(self) -> bool:
        if self.doc_a.id == self.doc_b.id:
            return False

        rule_sets = [
            "revised_document",
            "updated_document",
            "score_cosine_similarity",
            "score_euclidean_distance",
        ]
        match = False

        for rule_set in rule_sets:
            rule = getattr(self, rule_set)
            match = rule()
            if match:
                self.logger.info(f"matched rule '{rule_set}'")
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
            (self.filename_match >= 0.60 or self.element_text_match >= 0.90)
            and self.ref_indication_match >= 0.85
            and self.focus_therapy_match == 1
        )

    def score_euclidean_distance(self):
        return self.euclidean_distance < 2

    def score_cosine_similarity(self):
        return self.cosine_similarity > 0.9
