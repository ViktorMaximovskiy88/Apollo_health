import logging

from gensim.utils import simple_preprocess

from backend.common.core.enums import DocumentType
from backend.scrapeworker.common.utils import tokenize_filename, tokenize_url


class DocTypeMatcher:
    def __init__(
        self,
        raw_text: str,
        raw_link_text,
        raw_url: str,
        raw_name: str,
        take_count: int = 100,
    ):
        if raw_url:
            [*path_parts, filename] = tokenize_url(raw_url)
            self.filename_tokens = tokenize_filename(filename)
            self.filename_text = " ".join(self.filename_tokens).lower()
        else:
            self.filename_text = ""

        if raw_text:
            self.doc_tokens = simple_preprocess(raw_text)
            self.doc_tokens = self.doc_tokens[:take_count]
            self.doc_text = " ".join(self.doc_tokens).lower()
        else:
            self.doc_text = ""

        if raw_link_text:
            self.link_tokens = simple_preprocess(raw_link_text)
            self.link_text = " ".join(self.link_tokens).lower()
        else:
            self.link_text = ""

        if raw_name:
            self.name_tokens = simple_preprocess(raw_name)
            self.name_text = " ".join(self.name_tokens).lower()
        else:
            self.name_text = ""

        self.texts = [self.filename_text, self.doc_text, self.link_text, self.name_text]

        self.is_pennsylvania = False
        for text in self.texts:
            if "Pennsylvania" in text:
                self.is_pennsylvania = True
                break

        logging.info(
            f"link_text='{self.link_text}' name_text='{self.name_text}' filename_text='{self.filename_text}' doc_text='{self.doc_text}'"  # noqa
        )

    def _contains(self, text: str, terms: list[str]) -> bool:
        for term in terms:
            term = term.lower()
            if f" {text} ".find(f" {term} ") > -1:
                return True
        return False

    def _contains_all(self, text: str, terms: list[str]) -> bool:
        for term in terms:
            term = term.lower()
            if f" {text} ".find(f" {term} ") == -1:
                return False
        return True

    def formulary_update(self, text: str) -> str | None:
        if self._contains(text, ["PDL", "formulary", "drug list"]) and self._contains(
            text, ["update", "change"]
        ):
            return DocumentType.FormularyUpdate

    def formulary(self, text: str) -> str | None:
        if self._contains(text, ["PDL", "formulary", "drug list"]) and not self._contains(
            text, ["update", "change", "Preventive", "Specialty", "Exclusion", "Medical"]
        ):
            return DocumentType.Formulary

    def medical_coverage_list(self, text: str) -> str | None:
        if self._contains(text, ["Medical Coverage", "Jcode"]) and not self._contains(
            text, ["policy", "policies"]
        ):
            return DocumentType.MedicalCoverageList

    def restriction_list(self, text: str) -> str | None:
        if (
            (self._contains(text, ["PA"]) and not self.is_pennsylvania)
            or self._contains(text, ["Prior Authorization", "Authorization", "Auth"])
            or self._contains(text, ["ST", "Step Therapy", "Step-Therapy", "Step"])
            or self._contains(text, ["QL", "Quantity Limit", "Quantity"])
        ) and self._contains(text, ["list"]):
            return DocumentType.RestrictionList

    def specialty_list(self, text: str) -> str | None:
        if (self._contains(text, ["SP", "Specialty", "Specialty Pharmacy"])) and self._contains(
            text, ["list"]
        ):
            return DocumentType.SpecialtyList

    def exclusion_list(self, text: str) -> str | None:
        if (self._contains(text, ["Exclusion", "non-formulary"])) and self._contains(
            text, ["list"]
        ):
            return DocumentType.ExclusionList

    def preventive_drug_list(self, text: str) -> str | None:
        if (
            self._contains(
                text,
                [
                    "Preventive Drug",
                    "Preventive",
                    "Prevention",
                    "No Cost",
                    "Zero Copay",
                    "Zero Dollar Copay",
                    "$0 Copay",
                    "Zero Premium",
                ],
            )
        ) and self._contains(text, ["list"]):
            return DocumentType.PreventiveDrugList

    def fee_schedule(self, text: str) -> str | None:
        if self._contains(text, ["Fee Schedule"]):
            return DocumentType.FeeSchedule

    def authorization_policy_a(self, text: str) -> str | None:
        if (
            (self._contains(text, ["PA"]) and not self.is_pennsylvania)
            or self._contains(
                text,
                [
                    "Authorization",
                    "Auth",
                    "Step",
                    "ST",
                    "Prior Authorization",
                    "Step Therapy",
                ],
            )
        ) and not self._contains(text, ["list", "new to market", "unlisted", "non-formulary"]):
            return DocumentType.AuthorizationPolicy

    def site_of_care_policy(self, text: str) -> str | None:
        if self._contains(text, ["SOC", "site of care", "site-of-care"]):
            return DocumentType.SiteOfCarePolicy

    def authorization_policy_b(self, text: str) -> str | None:
        if self._contains(text, ["policy", "coverage determination"]) and not self._contains(
            text,
            [
                "update",
                "national",
                "local",
                "NCD",
                "LCD",
                "new to market",
                "unlisted",
                "non-formulary",
            ],
        ):
            return DocumentType.AuthorizationPolicy

    def authorization_policy_c(self, text: str) -> str | None:
        if self._contains(text, ["criteria"]) and not self._contains(
            text, ["new to market", "unlisted", "non-formulary"]
        ):
            return DocumentType.AuthorizationPolicy

    def new_to_market_policy(self, text: str) -> str | None:
        if self._contains(text, ["NTM", "new to market", "new-to-market"]) and not self._contains(
            text, ["policy", "guideline"]
        ):
            return DocumentType.NewToMarketPolicy

    def payer_unlisted_policy(self, text: str) -> str | None:
        if (
            self._contains(text, ["NF", "non-formulary", "unlisted"])
            and self._contains(text, ["policy", "guideline"])
            and not self._contains(text, ["NTM", "new to market", "new-to-market"])
        ):
            return DocumentType.PayerUnlistedPolicy

    def treatment_request_form(self, text: str) -> str | None:
        if self._contains(text, ["form", "request", "submission"]):
            return "Treatment Request Form"

    def provider_guide(self, text: str) -> str | None:
        if self._contains(
            text, ["Provider Policy", "Provider Manual", "Resource Manual", "Resource Guide"]
        ) or self._contains_all(text, ["Provider", "Guide"]):
            return DocumentType.ProviderGuide

    def evidence_of_coverage(self, text: str) -> str | None:
        if self._contains(text, ["EOC", "Evidence of Coverage"]):
            return DocumentType.EvidenceOfCoverage

    def summary_of_benefits(self, text: str) -> str | None:
        if self._contains(text, ["SOB", "Summary", "Benefits Summary", "Summary of Benefits"]):
            return DocumentType.SummaryOfBenefits

    def nccn_guidlines(self, text: str) -> str | None:
        if self._contains(text, ["NCCN", "NCCN Guideline", "Guideline"]):
            return DocumentType.NCCNGuideline

    def ncd(self, text: str) -> str | None:
        if self._contains(text, ["NCD", "national coverage determination"]):
            return DocumentType.NCD

    def lcd(self, text: str) -> str | None:
        if self._contains(text, ["LCD", "local coverage determination"]):
            return DocumentType.LCD

    def review_committee_meetings(self, text: str) -> str | None:
        if self._contains(
            text, ["Meeting", "Committee", "Agenda", "P&T", "Pharmacy & Therapeutics"]
        ) and not self._contains(text, ["schedule"]):
            return DocumentType.ReviewCommitteeMeetings

    def newsletter(self, text: str) -> str | None:
        if self._contains(text, ["Newsletter", "News"]):
            return DocumentType.Newsletter

    def review_committee_schedule(self, text: str) -> str | None:
        if self._contains(
            text, ["Meeting", "Committee", "Agenda", "P&T", "Pharmacy & Therapeutics"]
        ) and self._contains(text, ["schedule"]):
            return DocumentType.ReviewCommitteeSchedule

    def regulatory_document(self, text: str) -> str | None:
        if self._contains(text, ["regulation", "law", "carve out", "carve-out"]):
            return DocumentType.RegulatoryDocument

    def exec(self) -> str | None:

        if match := self.run_rules(self.link_text):
            logging.info("link_text matched")
            return match
        elif match := self.run_rules(self.name_text):
            logging.info("name_text matched")
            return match
        elif match := self.run_rules(self.filename_text):
            logging.info("filename_text matched")
            return match
        elif match := self.run_rules(self.doc_text):
            logging.info("doc_text matched")
            return match
        else:
            logging.info("No match fallthrough to classifier")
            return None

    def run_rules(self, text: str) -> str | None:
        # brute force, no lie... get fancy later
        # order matters
        rule_sets = [
            "formulary_update",
            "formulary",
            "medical_coverage_list",
            "restriction_list",
            "specialty_list",
            "exclusion_list",
            "preventive_drug_list",
            "fee_schedule",
            "authorization_policy_a",
            "site_of_care_policy",
            "authorization_policy_b",
            "authorization_policy_c",
            "new_to_market_policy",
            "payer_unlisted_policy",
            "treatment_request_form",
            "provider_guide",
            "evidence_of_coverage",
            "summary_of_benefits",
            "nccn_guidlines",
            "ncd",
            "lcd",
            "lcd",
            "review_committee_meetings",
            "newsletter",
            "review_committee_schedule",
            "regulatory_document",
        ]
        match = None

        for rule_set in rule_sets:
            rule = getattr(self, rule_set)
            match = rule(text)
            if match:
                logging.info(f"matched {rule_set}")
                break

        return match
