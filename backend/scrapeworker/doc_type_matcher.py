from gensim.utils import tokenize

from backend.scrapeworker.common.utils import tokenize_filename, tokenize_url


class DocTypeMatcher:
    def __init__(self, raw_text: str, raw_link_text, raw_url: str, take_count: int = 100):

        [*path_parts, filename] = tokenize_url(raw_url)
        self.filename_tokens = tokenize_filename(filename)
        self.filename_text = " ".join(self.filename_tokens)

        self.doc_tokens = [
            token for token in tokenize(raw_text, lower=False, deacc=True, errors="ignore")
        ]
        self.doc_tokens = self.doc_tokens[:take_count]
        self.doc_text = " ".join(self.doc_tokens)

        self.link_tokens = [
            token for token in tokenize(raw_link_text, lower=False, deacc=True, errors="ignore")
        ]
        self.link_text = " ".join(self.link_tokens)

    def _contains(self, text: str, terms: list[str]) -> bool:
        for term in terms:
            if text.find(f" {term} ") > -1:
                print(text, f"found '{term}'")
                return True
        return False

    def formulary_update(self, text: str) -> str | None:
        if self._contains(text, ["PDL", "formulary", "drug list"]) and self._contains(
            text, ["update", "change"]
        ):
            return "Formulary Update"

    def formulary(self, text: str) -> str | None:
        if self._contains(text, ["PDL", "formulary", "drug list"]) and not self._contains(
            text, ["update", "change", "Preventive", "Specialty", "Exclusion", "Medical"]
        ):
            return "Formulary"

    def medical_coverage_list(self, text: str) -> str | None:
        if self._contains(text, ["Medical Coverage", "Jcode"]) and not self._contains(
            text, ["policy", "policies"]
        ):
            return "Medical Coverage List"

    def restriction_list(self, text: str) -> str | None:
        if (
            self._contains(text, ["PA", "Prior Authorization", "Authorization", "Auth"])
            or self._contains(text, ["ST", "Step Therapy", "Step-Therapy", "Step"])
            or self._contains(text, ["QL", "Quantity Limit", "Quantity"]),
        ) and self._contains(text, ["list"]):
            return "Restriction List"

    def specialty_list(self, text: str) -> str | None:
        if (self._contains(text, ["SP", "Specialty", "Specialty Pharmacy"])) and self._contains(
            text, ["list"]
        ):
            return "Specialty List"

    def exclusion_list(self, text: str) -> str | None:
        if (self._contains(text, ["Exclusion", "non-formulary"])) and self._contains(
            text, ["list"]
        ):
            return "Exclusion List"

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
            return "Preventive Drug List"

    def fee_schedule(self, text: str) -> str | None:
        if self._contains(text, ["Fee Schedule"]):
            return "Fee Schedule"

    def authorization_policy_a(self, text: str) -> str | None:
        if self._contains(
            text,
            ["PA", "Authorization", "Auth", "Step", "ST", "Prior Authorization", "Step Therapy"],
        ) and not self._contains(text, ["list", "new to market", "unlisted", "non-formulary"]):
            return "Authorization Policy"

    def site_of_care_policy(self, text: str) -> str | None:
        if self._contains(text, ["SOC", "site of care", "site-of-care"]):
            return "Site of Care Policy"

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
            return "Authorization Policy"

    def authorization_policy_c(self, text: str) -> str | None:
        if self._contains(text, ["criteria"]) and not self._contains(
            text, ["new to market", "unlisted", "non-formulary"]
        ):
            return "Authorization Policy"

    def new_to_market_policy(self, text: str) -> str | None:
        if self._contains(text, ["NTM", "new to market", "new-to-market"]) and not self._contains(
            text, ["policy", "guideline"]
        ):
            return "New-to-Market Policy"

    def non_formulary_policy(self, text: str) -> str | None:
        if (
            self._contains(text, ["NF", "non-formulary", "unlisted"])
            and self._contains(text, ["policy", "guideline"])
            and not self._contains(text, ["NTM", "new to market", "new-to-market"])
        ):
            return "Non-formulary Policy"

    def treatment_request_form(self, text: str) -> str | None:
        if self._contains(text, ["form", "request", "submission"]):
            return "Treatment Request Form"

    def provider_guide(self, text: str) -> str | None:
        if self._contains(text, ["Provider Guide", "Provider Policy"]):
            return "Provider Guide"

    def evidence_of_coverage(self, text: str) -> str | None:
        if self._contains(text, ["EOC", "Evidence of Coverage"]):
            return "Evidence of Coverage"

    def summary_of_benefits(self, text: str) -> str | None:
        if self._contains(text, ["SOB", "Summary", "Benefits Summary", "Summary of Benefits"]):
            return "Summary of Benefits"

    def nccn_guidlines(self, text: str) -> str | None:
        if self._contains(text, ["NCCN", "NCCN Guidelines", "Guidelines"]):
            return "NCCN Guidelines"

    def ncd(self, text: str) -> str | None:
        if self._contains(text, ["NCD", "national coverage determination"]):
            return "NCD"

    def lcd(self, text: str) -> str | None:
        if self._contains(text, ["LCD", "local coverage determination"]):
            return "LCD"

    def review_committee_meetings(self, text: str) -> str | None:
        if self._contains(
            text, ["Meeting", "Committee", "Agenda", "P&T", "Pharmacy & Therapeutics"]
        ) and not self._contains(text, ["schedule"]):
            return "Review Committee Meetings"

    def newsletter(self, text: str) -> str | None:
        if self._contains(text, ["Newsletter", "News"]):
            return "Newsletter"

    def review_committee_schedule(self, text: str) -> str | None:
        if self._contains(
            text, ["Meeting", "Committee", "Agenda", "P&T", "Pharmacy & Therapeutics"]
        ) and self._contains(text, ["schedule"]):
            return "Review Committee Schedule"

    def regulation(self, text: str) -> str | None:
        if self._contains(text, ["regulation", "law", "carve out", "carve-out"]):
            return "Regulation"

    def exec(self) -> str | None:

        if match := self.run_rules(self.link_text):
            return match
        elif match := self.run_rules(self.filename_text):
            return match
        elif match := self.run_rules(self.doc_text):
            return match
        else:
            return None

    def run_rules(self, text: str) -> str | None:
        # take first 500 chars...
        # brute force, no lie... get fancy later
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
            "non_formulary_policy",
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
            "regulation",
        ]
        match = None

        for rule_set in rule_sets:
            rule = getattr(self, rule_set)
            match = rule(text)
            if match:
                print(f"matched {rule_set} {text}")
                break

        return match
