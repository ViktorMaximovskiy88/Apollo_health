import re
import tempfile

from scispacy.candidate_generation import (
    DEFAULT_KNOWLEDGE_BASES,
    DEFAULT_PATHS,
    CandidateGenerator,
    LinkerPaths,
    MentionCandidate,
)
from scispacy.linking_utils import KnowledgeBase

from backend.common.models.translation_config import TranslationRule
from backend.common.storage.client import ModelStorageClient


class RxNormEntityLinkerModel:
    def __init__(self, version="latest"):
        try:
            self.client = ModelStorageClient()
            self.tempdir = tempfile.TemporaryDirectory()
            dirname = self.tempdir.name
            self.client.download_directory(f"rxnorm/{version}", dirname)
        except Exception:
            print("RxNorm model not found and therefore not loaded")
            return

        try:
            DEFAULT_PATHS[f"RxNorm_{version}"] = LinkerPaths(
                ann_index=f"{dirname}/nmslib_index.bin",
                tfidf_vectorizer=f"{dirname}/tfidf_vectorizer.joblib",
                tfidf_vectors=f"{dirname}/tfidf_vectors_sparse.npz",
                concept_aliases_list=f"{dirname}/concept_aliases.json",
            )

            class RxNormKnowledgeBase(KnowledgeBase):
                def __init__(self):
                    super().__init__(f"{dirname}/rxnorm.jsonl")

            DEFAULT_KNOWLEDGE_BASES[f"RxNorm_{version}"] = RxNormKnowledgeBase
            self.linker = CandidateGenerator(name=f"RxNorm_{version}")  # type: ignore
        except Exception:
            print("RxNorm Entity Linker Model Not Found")
            return

    form_abbr = [
        (r"\btabs?\b", "tablet"),
        (r"\bcaps?\b", "capsule"),
        (r"\bsoln\b", "solution"),
        (r"\bdr\b", "delayed release"),
        (r"\ber\b", "extended release"),
        (r"\ber\b", "extended release"),
        (r"\bliqd\b", "liquid"),
        (r"\bprsyr\b", "prefilled syringe"),
        (r"\bsuppos\b", "suppository"),
        (r"\bsusp\b", "suspension"),
        (r"\bconc\b", "concentrate"),
        (r"\boint\b", "ointment"),
    ]
    form_abbr = [(re.compile(rgx, re.IGNORECASE), st) for rgx, st in form_abbr]

    NUMBER_REGEX = re.compile(r"\d\d*(?:\.\d+)?")

    def preprocess(self, texts: list[str | None], rule: TranslationRule):
        new_texts: list[str] = []
        for text in texts:
            if text is None:
                text = ""
            for rgx, st in self.form_abbr:
                text = re.sub(rgx, st, text)
            text = text.replace("\n", " ")

            if rule.separator:
                splits = text.split(rule.separator)
                name, strengths = splits[0], splits[1:]
                name_and_first_strength = re.split(r"(\d\d*(?:\.\d+)?)", name, 1)
                if len(name_and_first_strength) > 1:
                    name, first_strength, unit = name_and_first_strength
                    strengths.insert(0, first_strength + unit)
                else:
                    strengths.insert(0, "")

                for strength in strengths:
                    new_texts.append(name + strength)
            else:
                new_texts.append(text)
        return new_texts

    def find_candidates(
        self,
        texts: list[str | None],
        rule: TranslationRule,
    ) -> list[tuple[str, MentionCandidate | None, str, float]]:
        if not self.linker:
            return []

        clean_texts = self.preprocess(texts, rule)
        candidate_list = self.linker(clean_texts, 20)
        best_candidates: list[tuple[str, MentionCandidate | None, str, float]] = []
        for span, candidates in zip(clean_texts, candidate_list):
            if not span:
                continue

            best_score = 0
            best_description = ""
            best_candidate: MentionCandidate | None = None
            for candidate in candidates:
                max_similarity = max(candidate.similarities)
                description = candidate.aliases[candidate.similarities.index(max_similarity)]

                if max_similarity > best_score:
                    best_score = max_similarity
                    best_description = description
                    best_candidate = candidate
            best_candidates.append((span, best_candidate, best_description, best_score))

        return best_candidates


rxnorm_linker = RxNormEntityLinkerModel()
