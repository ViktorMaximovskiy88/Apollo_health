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

        self.name_text_match = jarowinkler_similarity(doc_a.name, doc_b.name)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' name_text_match={self.name_text_match}"
        )

        self.element_text_match = jarowinkler_similarity(doc_a.element_text, doc_b.element_text)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' element_text_match={self.element_text_match}"
        )

        self.parent_text_match = jarowinkler_similarity(doc_a.parent_text, doc_b.parent_text)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' parent_text_match={self.parent_text_match}"
        )

        self.siblings_text_match = jarowinkler_similarity(doc_a.siblings_text, doc_b.siblings_text)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' siblings_text_match={self.siblings_text_match}"
        )

        self.filename_match = jaccard(doc_a.filename_tokens, doc_b.filename_tokens)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' filename_match={self.filename_match}"
        )

        self.pathname_match = jaccard(doc_a.pathname_tokens, doc_b.pathname_tokens)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' pathname_match={self.pathname_match}"
        )

        self.ref_indication_match = jaccard(doc_a.ref_indication_tags, doc_b.ref_indication_tags)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' ref_indication_match={self.ref_indication_match}"
        )

        self.focus_indication_match = jaccard(
            doc_a.focus_indication_tags, doc_b.focus_indication_tags
        )
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' focus_indication_match={self.focus_indication_match}"
        )

        self.ref_therapy_match = jaccard(doc_a.ref_therapy_tags, doc_b.ref_therapy_tags)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' ref_therapy_match={self.ref_therapy_match}"
        )

        self.focus_therapy_match = jaccard(doc_a.focus_therapy_tags, doc_b.focus_therapy_tags)
        self.logger.debug(
            f"'{self.doc_a.name}' '{self.doc_b.name}' focus_therapy_match={self.focus_therapy_match}"
        )

        self.url_focus_therapy_match = jaccard(
            doc_a.url_focus_therapy_tags, doc_b.url_focus_therapy_tags
        )
        self.url_focus_indication_match = jaccard(
            doc_a.url_focus_indication_tags, doc_b.url_focus_indication_tags
        )

        self.link_focus_therapy_match = jaccard(
            doc_a.link_focus_therapy_tags, doc_b.link_focus_therapy_tags
        )
        self.link_focus_indication_match = jaccard(
            doc_a.link_focus_indication_tags, doc_b.link_focus_indication_tags
        )

        if len(self.doc_a.doc_vectors) == 0 or len(self.doc_b.doc_vectors) == 0:
            self.logger.debug(f"'{self.doc_a.name}' len(doc_vectors)={len(self.doc_a.doc_vectors)}")
            self.logger.debug(f"'{self.doc_b.name}' len(doc_vectors)={len(self.doc_b.doc_vectors)}")
            self.cosine_similarity = 0
            self.euclidean_distance = 100
        else:
            self.cosine_similarity = 1 - spatial.distance.cosine(
                self.doc_a.doc_vectors[0],
                self.doc_b.doc_vectors[0],
            )
            self.logger.debug(
                f"'{self.doc_a.name}' '{self.doc_b.name}' self.cosine_similarity={self.cosine_similarity}"
            )
            self.euclidean_distance = spatial.distance.euclidean(
                self.doc_a.doc_vectors[0],
                self.doc_b.doc_vectors[0],
            )
            self.logger.debug(
                f"'{self.doc_a.name}' '{self.doc_b.name}' self.euclidean_distance={self.euclidean_distance}"
            )

    def exec(self) -> bool:
        if self.doc_a.id == self.doc_b.id:
            return False

        rule_sets = [
            "revised_document",
            "updated_document_b",
            "updated_document_a",
            "updated_document_c",
            "similar_rule",
        ]
        match = False

        for rule_set in rule_sets:
            rule = getattr(self, rule_set)
            match = rule()
            if match:
                self.logger.info(
                    f"'{self.doc_a.name}' '{self.doc_b.name}' matched rule '{rule_set}'"
                )
                break

        return match

    ###
    # Rule sets: have precedence and are composed of rules (tbd refactor)
    ###
    # same base url, same url, same doc, new doc revision/updated
    def revised_document(self):
        return (
            # same name or url exact match
            (self.name_text_match == 1 or (self.filename_match == 1 and self.pathname_match == 1))
            # focus exact match on link or url
            and self.url_therapy_match_rule(1)
            and self.link_therapy_match_rule(1)
            and self.state_abbr_rule()
            and self.state_name_rule()
        )

    # strict context with less tag assuredness
    def updated_document_a(self):
        return (
            self.url_therapy_match_rule(1)
            and self.link_therapy_match_rule(1)
            and self.state_abbr_rule()
            and self.state_name_rule()
        )

    # looser context with stricter tag assuredness
    def updated_document_b(self):
        return (
            (self.filename_match >= 0.60 or self.element_text_match >= 0.90)
            and self.url_therapy_match_rule(1)
            and self.link_therapy_match_rule(1)
            and self.state_abbr_rule()
            and self.state_name_rule()
        )

    # looser context with no tag assuredness
    def updated_document_c(self):
        return (
            (self.filename_match >= 0.90 or self.element_text_match >= 0.90)
            and self.score_cosine_similarity()
            and self.state_abbr_rule()
            and self.state_name_rule()
        )

    def require_url_indication_match(self):
        return len(self.doc_a.url_focus_indication_tags) > 0 or len(
            self.doc_b.url_focus_indication_tags
        )

    def require_url_therapy_match(self):
        return len(self.doc_a.url_focus_therapy_tags) > 0 or len(self.doc_b.url_focus_therapy_tags)

    def require_link_indication_match(self):
        return len(self.doc_a.link_focus_indication_tags) > 0 or len(
            self.doc_b.link_focus_indication_tags
        )

    def require_link_therapy_match(self):
        return len(self.doc_a.link_focus_therapy_tags) > 0 or len(
            self.doc_b.link_focus_therapy_tags
        )

    def link_therapy_match_rule(self, threshhold: int = 1):
        return self.require_link_therapy_match() and self.link_focus_therapy_match == threshhold

    def link_indication_match_rule(self, threshhold: int = 1):
        return (
            self.require_link_indication_match() and self.link_focus_indication_match == threshhold
        )

    def url_therapy_match_rule(self, threshhold: int = 1):
        return self.require_url_therapy_match() and self.url_focus_therapy_match == threshhold

    def url_indication_match_rule(self, threshhold: int = 1):
        return self.require_url_indication_match() and self.url_focus_indication_match == threshhold

    def require_state_name(self):
        return self.doc_a.state_name or self.doc_a.state_name

    def require_state_abbr(self):
        return self.doc_a.state_abbr or self.doc_a.state_abbr

    def state_name_match(self):
        return self.doc_a.state_name == self.doc_b.state_name

    def state_abbr_match(self):
        return self.doc_a.state_abbr == self.doc_b.state_abbr

    def require_year_part(self):
        return self.doc_a.year_part and self.doc_a.year_part

    def state_abbr_rule(self):
        return (
            self.require_state_abbr() and self.state_abbr_match()
        ) or not self.require_state_abbr()

    def state_name_rule(self):
        return (
            self.require_state_name() and self.state_name_match()
        ) or not self.require_state_name()

    def similar_rule(self):
        return (
            self.euclidean_distance < 2
            and self.state_abbr_rule()
            and self.require_year_part()
            and self.state_name_rule()
        )

    def score_euclidean_distance(self):
        return self.euclidean_distance < 2

    def score_cosine_similarity(self):
        return self.cosine_similarity > 0.9
