class DocTypeMatcher:
    def __init__(self, text: str, take_count: int = 500, lower=True):
        self.text = text[:take_count]
        self.lower = lower

    def _contains(self, terms: list[str]) -> bool:
        for term in terms:
            term = term.lower() if self.lower else term
            if self.text.find(term):
                return True
        return False

    def formulary_update(self) -> str | None:
        if self._contains(["PDL", "formulary", "drug list"]) and self._contains(
            ["update", "change"]
        ):
            return "Formulary Update"

    def formulary(self) -> str | None:
        if self._contains(["PDL", "formulary", "drug list"]) and not self._contains(
            ["update", "change", "Preventive", "Specialty", "Exclusion", "Medical"]
        ):
            return "Formulary"

    def medical_coverage_list(self) -> str | None:
        if self._contains(["Medical Coverage", "Jcode"]) and not self._contains(
            ["policy", "policies"]
        ):
            return "Medical Coverage List"

    def restriction_list(self) -> str | None:
        if (
            self._contains(["PA", "Prior Authorization", "Authorization", "Auth"])
            or self._contains(["ST", "Step Therapy", "Step-Therapy", "Step"])
            or self._contains(["QL", "Quantity Limit", "Quantity"]),
        ) and self._contains(["list"]):
            return "Restriction List"

    def specialty_list(self) -> str | None:
        if (self._contains(["SP", "Specialty", "Specialty Pharmacy"])) and self._contains(["list"]):
            return "Specialty List"

    def exclusion_list(self) -> str | None:
        if (self._contains(["Exclusion", "non-formulary"])) and self._contains(["list"]):
            return "Exclusion List"

    def preventive_drug_list(self) -> str | None:
        if (
            self._contains(
                [
                    "Preventive Drug",
                    "Preventive",
                    "Prevention",
                    "No Cost",
                    "Zero Copay",
                    "Zero Dollar Copay",
                    "$0 Copay",
                    "Zero Premium",
                ]
            )
        ) and self._contains(["list"]):
            return "Preventive Drug List"

    def fee_schedule(self) -> str | None:
        if self._contains(["Fee Schedule"]):
            return "Fee Schedule"

    def authorization_policy_a(self) -> str | None:
        if self._contains(
            ["PA", "Authorization", "Auth", "Step", "ST", "Prior Authorization", "Step Therapy"]
        ) and not self._contains(["list", "new to market", "unlisted", "non-formulary"]):
            return "Authorization Policy"

    def site_of_care_policy(self) -> str | None:
        if self._contains(["SOC", "site of care", "site-of-care"]):
            return "Site of Care Policy"

    def authorization_policy_b(self) -> str | None:
        if self._contains(["policy", "coverage determination"]) and not self._contains(
            [
                "update",
                "national",
                "local",
                "NCD",
                "LCD",
                "new to market",
                "unlisted",
                "non-formulary",
            ]
        ):
            return "Authorization Policy"

    def authorization_policy_c(self) -> str | None:
        if self._contains(["criteria"]) and not self._contains(
            ["new to market", "unlisted", "non-formulary"]
        ):
            return "Authorization Policy"

    def new_to_market_policy(self) -> str | None:
        if self._contains(["NTM", "new to market", "new-to-market"]) and not self._contains(
            ["policy", "guideline"]
        ):
            return "New-to-Market Policy"

    def non_formulary_policy(self) -> str | None:
        if (
            self._contains(["NF", "non-formulary", "unlisted"])
            and self._contains(["policy", "guideline"])
            and not self._contains(["NTM", "new to market", "new-to-market"])
        ):
            return "Non-formulary Policy"

    def treatment_request_form(self) -> str | None:
        if self._contains(["form", "request", "submission"]):
            return "Treatment Request Form"

    def provider_guide(self) -> str | None:
        if self._contains(["Provider Guide", "Provider Policy"]):
            return "Provider Guide"

    def evidence_of_coverage(self) -> str | None:
        if self._contains(["EOC", "Evidence of Coverage"]):
            return "Evidence of Coverage"

    def summary_of_benefits(self) -> str | None:
        if self._contains(["SOB", "Summary", "Benefits Summary", "Summary of Benefits"]):
            return "Summary of Benefits"

    def nccn_guidlines(self) -> str | None:
        if self._contains(["NCCN", "NCCN Guidelines", "Guidelines"]):
            return "NCCN Guidelines"

    def ncd(self) -> str | None:
        if self._contains(["NCD", "national coverage determination"]):
            return "NCD"

    def lcd(self) -> str | None:
        if self._contains(["LCD", "local coverage determination"]):
            return "LCD"

    def review_committee_meetings(self) -> str | None:
        if self._contains(
            ["Meeting", "Committee", "Agenda", "P&T", "Pharmacy & Therapeutics"]
        ) and not self._contains(["schedule"]):
            return "Review Committee Meetings"

    def newsletter(self) -> str | None:
        if self._contains(["Newsletter", "News"]):
            return "Newsletter"

    def review_committee_schedule(self) -> str | None:
        if self._contains(
            ["Meeting", "Committee", "Agenda", "P&T", "Pharmacy & Therapeutics"]
        ) and self._contains(["schedule"]):
            return "Review Committee Schedule"

    def regulation(self) -> str | None:
        if self._contains(["regulation", "law", "carve out", "carve-out"]):
            return "Regulation"

    def exec(self) -> str | None:
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
            match = rule()
            if match:
                break

        return match
