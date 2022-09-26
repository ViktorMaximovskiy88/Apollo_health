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
        self.linker = None
        try:
            self.client = ModelStorageClient()
            self.tempdir = tempfile.TemporaryDirectory()
            dirname = self.tempdir.name
            self.client.download_directory(f"rxnorm/{version}", dirname)
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
        (r"\bca?ps?\b", "capsule"),
        (r"\bcp24\b", "capsule extended release"),
        (r"\b12.hour\b", "12 HR extended release"),
        (r"\b24.hour\b", "24 HR extended release"),
        (r"\bsoln\b", "solution"),
        (r"\bdr\b", "delayed release"),
        (r"\ber\b", "extended release"),
        (r"\bxr\b", "extended release"),
        (r"\bcr\b", "extended release"),
        (r"\bcontrolled release\b", "extended release"),
        (r"\bsl\b", "sublingual"),
        (r"\bliqd\b", "liquid"),
        (r"\binj\b", "injection"),
        (r"\bconc\b", "concentrate"),
        (r"\bprsyr\b", "prefilled syringe"),
        (r"\bpref\b", "prefilled"),
        (r"\bsuppos\b", "suppository"),
        (r"\bsusp\b", "suspension"),
        (r"\bconc\b", "concentrate"),
        (r"\boint\b", "ointment"),
        (r"\bophth\b", "ophthalmic"),
        (r"\bim\b", "intramuscular"),
        (r"\bact\b", "actuation"),
        (r"\bactuat\b", "actuation"),
        (r"\bpow\b", "powder"),
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
            text = re.sub(r"\s+", " ", text)

            if rule.separator:
                splits = re.split(f"[{rule.separator}]", text)
                name, strengths = splits[0], splits[1:]
                name_and_first_strength = re.split(r"(\d\d*(?:\.\d+)?)", name, 1)
                if len(name_and_first_strength) > 1:
                    name, first_strength, unit = name_and_first_strength
                    strengths.insert(0, first_strength + unit)
                else:
                    strengths.insert(0, "")

                for strength in strengths:
                    new_texts.append(f"{name.strip()} {strength.strip()}")
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
            has_bulk = "bulk" in span.lower()

            numerics = set(re.findall(self.NUMBER_REGEX, span))

            best_score = 0
            best_description = ""
            best_candidate: MentionCandidate | None = None
            for candidate in candidates:
                for score, description in zip(candidate.similarities, candidate.aliases):
                    if score < 0.5:
                        continue
                    if "bulk" in description.lower() and not has_bulk:
                        continue

                    candidate_numerics = set(re.findall(self.NUMBER_REGEX, description))
                    score += len(numerics.intersection(candidate_numerics))
                    score -= len(numerics.symmetric_difference(candidate_numerics))

                    if score > best_score:
                        best_score = score
                        best_description = description
                        best_candidate = candidate

            best_candidates.append((span, best_candidate, best_description, best_score))

        return best_candidates


rxnorm_linker = RxNormEntityLinkerModel()
