from functools import cached_property, lru_cache
from urllib.parse import unquote

import numpy as np
from gensim.utils import simple_preprocess
from jarowinkler import jarowinkler_similarity
from rapidfuzz import fuzz
from scipy import spatial

from backend.common.models.lineage import DocumentAnalysis, DocumentAttrs
from backend.scrapeworker.common.utils import jaccard


class LineagePreprocessor:
    def keywords(self):
        pa_st = [
            ["pa", "prior authorization"],
            ["st", "step therapy"],
        ]
        routes = [
            ["oral"],
            ["sublingual"],
            ["buccal"],
            ["im", "instramuscular"],
            ["iv", "intravenous"],
            ["sq", "subcutaneous"],
            ["rectal"],
            ["vaginal"],
            ["intranasal"],
            ["inhalation"],
        ]
        plan_types = [
            ["hmo"],
            ["ppo"],
            ["pos"],
            ["pdp"],
            ["hix"],
            ["ma"],
            ["pd"],
            ["medicaid"],
            ["medicare"],
            ["part d"],
        ]
        return pa_st + routes + plan_types

    @lru_cache(1000)
    def tokenize(self, text: str) -> tuple[str]:
        return tuple(simple_preprocess(text))

    @lru_cache(1000)
    def presence_of_keywords(self, text_tokens: list[str]):
        poks = []
        for tokens in self.keywords():
            poks.append(int(any(t in text_tokens for t in tokens)))
        return poks

    def text_features(
        self,
        text1: str | None,
        text2: str | None,
        attrs1: DocumentAttrs | None = None,
        attrs2: DocumentAttrs | None = None,
    ):
        features = []
        if text1 and text2:
            text1, text2 = unquote(text1), unquote(text2)
            features.append(fuzz.token_set_ratio(text1, text2))
            features.append(jarowinkler_similarity(text1, text2))

            tokens1, tokens2 = self.tokenize(text1), self.tokenize(text2)
            poks1 = self.presence_of_keywords(tokens1)
            poks2 = self.presence_of_keywords(tokens2)
            for pok1, pok2 in zip(poks1, poks2):
                features.append(pok1)
                features.append(pok2)
        else:
            # Note: 4*[0] in python is [0,0,0,0]
            features += [0, 0] + 2 * len(self.keywords()) * [0]

        if attrs1 and attrs2:
            features.append(bool(attrs1.state_name and attrs2.state_name))
            features.append(int(attrs1.state_name == attrs2.state_name))
            features.append(bool(attrs1.state_abbr and attrs2.state_abbr))
            features.append(int(attrs1.state_abbr == attrs2.state_abbr))
            features.append(int(attrs1.month_name == attrs2.month_name))
            features.append(int(attrs1.month_abbr == attrs2.month_abbr))
            features.append(bool(attrs1.year_part) ^ bool(attrs2.year_part))
            features.append(abs((attrs1.year_part or 0) - (attrs2.year_part or 0)))
            features.append(int(attrs1.lang_code == attrs2.lang_code))
        return features

    def tag_features(self, tags1: list[str | int] | list[int], tags2: list[str | int] | list[int]):
        return [
            len(tags1),
            len(tags2),
            jaccard(tags1, tags2),
        ]

    @property
    def n_columns(self):
        return len(self.column_names)

    def text_feature_names(self, name, has_attr=True):
        feature_names = [f"{name}_token_set_ratio", f"{name}_jw_similarity"]
        for tokens in self.keywords():
            feature_names += [f"{name}_{tokens[0]}_1", f"{name}_{tokens[0]}_2"]
        if has_attr:
            feature_names += [
                f"{name}_has_state_name",
                f"{name}_state_name",
                f"{name}_has_state_abbr",
                f"{name}_state_abbr",
                f"{name}_month_name",
                f"{name}_month_abbr",
                f"{name}_year_xor",
                f"{name}_year_diff",
                f"{name}_lang_code",
            ]
        return feature_names

    def tag_feature_names(self, name):
        return [
            f"{name}_tag1_count",
            f"{name}_tag2_count",
            f"{name}_jaccard",
        ]

    @cached_property
    def column_names(self):
        names = [
            "d1_file_size",
            "d1_token_count",
            "d2_file_size",
            "d2_token_count",
            "vector_cosine",
            "vector_euclidean",
        ]
        names += self.text_feature_names("name", False)
        names += self.text_feature_names("element")
        names += self.text_feature_names("parent")
        names += self.text_feature_names("siblings")
        names += self.text_feature_names("filename")
        names += self.text_feature_names("pathname")
        names += self.tag_feature_names("ref_ind")
        names += self.tag_feature_names("foc_ind")
        names += self.tag_feature_names("url_foc_ind")
        names += self.tag_feature_names("link_foc_ind")
        names += self.tag_feature_names("ref_ther")
        names += self.tag_feature_names("foc_ther")
        names += self.tag_feature_names("url_foc_ther")
        names += self.tag_feature_names("link_foc_ther")
        return names

    def preprocess(self, doc1: DocumentAnalysis, doc2: DocumentAnalysis):
        feature_sets = []
        feature_sets.append(self.text_features(doc1.name, doc2.name))
        feature_sets.append(
            self.text_features(doc1.element_text, doc2.element_text, doc1.element, doc2.element)
        )
        feature_sets.append(
            self.text_features(doc1.parent_text, doc2.parent_text, doc1.parent, doc2.parent)
        )
        feature_sets.append(
            self.text_features(doc1.siblings_text, doc2.siblings_text, doc1.siblings, doc2.siblings)
        )
        feature_sets.append(
            self.text_features(doc1.filename_text, doc2.filename_text, doc1.filename, doc2.filename)
        )
        feature_sets.append(
            self.text_features(doc1.pathname_text, doc2.pathname_text, doc1.pathname, doc2.pathname)
        )

        feature_sets.append(self.tag_features(doc1.ref_indication_tags, doc2.ref_indication_tags))
        feature_sets.append(
            self.tag_features(doc1.focus_indication_tags, doc2.focus_indication_tags)
        )
        feature_sets.append(
            self.tag_features(doc1.url_focus_indication_tags, doc2.url_focus_indication_tags)
        )
        feature_sets.append(
            self.tag_features(doc1.link_focus_indication_tags, doc2.link_focus_indication_tags)
        )

        feature_sets.append(self.tag_features(doc1.ref_therapy_tags, doc2.ref_therapy_tags))
        feature_sets.append(self.tag_features(doc1.focus_therapy_tags, doc2.focus_therapy_tags))
        feature_sets.append(
            self.tag_features(doc1.url_focus_therapy_tags, doc2.url_focus_therapy_tags)
        )
        feature_sets.append(
            self.tag_features(doc1.link_focus_therapy_tags, doc2.link_focus_therapy_tags)
        )

        features = np.zeros(self.n_columns, dtype=np.float32)
        features[0] = doc1.file_size
        features[1] = doc1.token_count
        features[2] = doc2.file_size
        features[3] = doc2.token_count
        features[4] = 0
        features[5] = -1
        if doc1.doc_vectors and doc2.doc_vectors:
            v1 = doc1.doc_vectors[0]
            v2 = doc2.doc_vectors[0]
            if len(v1) == len(v2):
                features[4] = spatial.distance.cosine(v1, v2)
                features[5] = spatial.distance.euclidean(v1, v2)

        i = 6
        for feature_set in feature_sets:
            for feature in feature_set:
                features[i] = feature
                i += 1
        return features
