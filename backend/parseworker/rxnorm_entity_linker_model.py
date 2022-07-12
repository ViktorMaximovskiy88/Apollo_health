import re
from scispacy.linking_utils import KnowledgeBase
import tempfile
from scispacy.candidate_generation import DEFAULT_PATHS, DEFAULT_KNOWLEDGE_BASES
from scispacy.candidate_generation import (
    CandidateGenerator,
    MentionCandidate,
    LinkerPaths
)
from backend.common.storage.client import ModelStorageClient

class RxNormEntityLinkerModel():
    def __init__(self, version = 'latest'):
        self.version = version
        self.client = ModelStorageClient()
        self.tempdir = tempfile.TemporaryDirectory()
        dirname = self.tempdir.name
        try:
            self.client.download_directory(f'rxnorm/{version}', dirname)
        except:
            print(f"RxNorm model not found and therefore not loaded")
            return

        DEFAULT_PATHS[f'RxNorm_{version}'] = LinkerPaths(
            ann_index=f"{dirname}/nmslib_index.bin",
            tfidf_vectorizer=f"{dirname}/tfidf_vectorizer.joblib",
            tfidf_vectors=f"{dirname}/tfidf_vectors_sparse.npz",
            concept_aliases_list=f"{dirname}/concept_aliases.json",
        )
        class RxNormKnowledgeBase(KnowledgeBase):
            def __init__(self):
                super().__init__(f'{dirname}/rxnorm.jsonl')
        DEFAULT_KNOWLEDGE_BASES[f'RxNorm_{version}'] = RxNormKnowledgeBase
        self.linker = CandidateGenerator(name=f"RxNorm_{version}")  # type: ignore
    
    form_abbr = [
        (r'\btab\b', 'tablet'),
        (r'\bcap\b', 'capsule'),
        (r'\bsoln\b', 'solution'),
        (r'\bdr\b', 'delayed release'),
        (r'\ber\b', 'extended release'),
        (r'\ber\b', 'extended release'),
        (r'\bliqd\b', 'liquid'),
        (r'\bprsyr\b', 'prefilled syringe'),
        (r'\bsuppos\b', 'suppository'),
        (r'\bsusp\b', 'suspension'),
        (r'\bconc\b', 'concentrate'),
        (r'\boint\b', 'ointment'),
    ]
    form_abbr = [(re.compile(rgx, re.IGNORECASE), st) for rgx,st in form_abbr]
    def preprocess(self, texts):
        new_texts = []
        for text in texts:
            if text is None: text = ''
            for rgx, st in self.form_abbr:
                text = re.sub(rgx, st, text)
            new_texts.append(text.replace('\n', ' '))
        return new_texts
    
    NUMBER_REGEX = re.compile(r"\d\d*(?:\.\d+)?")
    def find_candidates(self, texts: list[str]) -> list[tuple[str, MentionCandidate | None, str, float]]:
        if not self.linker:
            return []

        texts = self.preprocess(texts)
        candidate_list = self.linker(texts, 20)
        best_candidates: list[tuple[str, MentionCandidate | None, str, float]] = []
        for span, candidates in zip(texts, candidate_list):
            numbers = set(self.NUMBER_REGEX.findall(span))
            best_score = 0
            best_description = ''
            best_candidate: MentionCandidate | None = None
            for candidate in candidates:
                max_similarity = max(candidate.similarities)
                description = candidate.aliases[candidate.similarities.index(max_similarity)]
                desc_numbers = set(self.NUMBER_REGEX.findall(description))
                if numbers != desc_numbers:
                    continue

                if max_similarity > best_score:
                    best_score = max_similarity
                    best_description = description
                    best_candidate = candidate
            best_candidates.append((span, best_candidate, best_description, best_score))

        return best_candidates
    