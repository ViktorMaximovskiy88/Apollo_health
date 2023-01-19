from playwright.async_api import Error, TimeoutError

from backend.common.core.enums import ScrapeMethod
from backend.common.models.app_config import AppConfig
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class TricareScraper(PlaywrightBaseScraper):

    type: str = "Tricare"

    def css_selector(self) -> str:
        return ""

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.scrape_method == ScrapeMethod.Tricare
        self.log.debug(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        timeout = self.config.wait_for_timeout_ms
        tricare_url = "https://www.express-scripts.com/frontend/open-enrollment/tricare/fst/#/"

        search_terms = await AppConfig.get_tricare_tokens()
        prefix_terms = set()

        prefix_length = 4
        for term in search_terms:
            prefix_term = term[:prefix_length].lower()
            if prefix_term in prefix_terms or len(prefix_term) < prefix_length:
                continue

            prefix_terms.add(prefix_term)

        prefix_terms = list(prefix_terms)
        prefix_terms.sort()

        try:
            await self.page.goto(tricare_url)
            await self.page.locator("#formularySearchDefault").wait_for(timeout=timeout)

            # # step 1: get search term data from typeahead
            search_results = await self._search_for_terms(prefix_terms)
            self.log.debug(f"search_results={len(search_results)} found")

            unique_urls = set()
            # step 2: get search results from price API
            for search_params in search_results:
                pricing_result = await self._get_search_term_pricing(search_params)
                self.log.debug(
                    f"found pricing_result={pricing_result} search_params={search_params}",
                )

                is_covered = pricing_result and pricing_result.get("drugCovered", False)
                if not is_covered:
                    continue

                pricing_result["ndc"] = search_params["ndc"]
                pricing_result["hicl"] = search_params["hicl"]
                pricing_result["gcn"] = search_params["gcn"]
                pricing_result["specificTherapeuticClassCode"] = search_params[
                    "specificTherapeuticClassCode"
                ]

                # step 3: get content aka docs
                documents = await self._get_document_list(pricing_result)
                self.log.debug(f"documents={len(documents)} found")

                for document in documents:
                    url = "https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/forms/content"  # noqa
                    url += f"?repository={document['repository']}&documentId={document['documentId']}"  # noqa
                    if url not in unique_urls:

                        unique_urls.add(url)
                        cookies = await self.context.cookies(self.page.url)

                        downloads.append(
                            DownloadContext(
                                metadata=Metadata(
                                    link_text=f"{search_params['drug_name']} {document['type']}",
                                    base_url=self.page.url,
                                ),
                                request=Request(
                                    url=url,
                                    cookies=cookies,
                                ),
                            )
                        )
        except TimeoutError as ex:
            self.log.error("tricare", exc_info=ex)
        except Error as ex:
            self.log.error("tricare", exc_info=ex)

        return downloads

    async def _search_for_terms(self, search_terms: list[str]) -> list[dict]:
        results = {}
        for search_term in search_terms:
            search_url = f"https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/search?name={search_term}&context=fst"  # noqa
            response = await self.page.request.get(search_url)
            search_results = await response.json()
            await self.page.wait_for_timeout(900)

            if not isinstance(search_results, list) or len(search_results) == 0:
                self.log.debug(f"no results for search_term={search_term}")
                continue

            self.log.debug(f"search_term={search_term} result={len(search_results)}")

            for search_result in search_results:
                ndc = search_result["ndc"]
                if not results.get(ndc, None):
                    search_result["search_token"] = search_term
                    results[ndc] = search_result

        return [self._map_seach_result(result) for result in results.values()]

    async def _get_search_term_pricing(self, params: dict):

        request_data = {
            "drugNdc": params["ndc"],
            "packagedDrug": params["isPackagedDrug"],
            "metricSize": params["metricSize"],
            "units": params["units"],
            "frequency": params["frequency"],
            "multiSourceDrug": params["isMultiSourceDrug"],
            "drugTypeLabel": params["drugTypeLabel"],
            "patientAge": "18",
            "patientGender": "female",
            "includeMailPricing": True,
        }

        url = "https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/pricing"  # noqa
        response = await self.page.request.post(url, data=request_data)
        result = await response.json()
        await self.page.wait_for_timeout(900)

        if self._has_valid_pricing(result):
            return self._map_pricing_result(result["mailPricing"], result["retailPricings"][0])
        else:
            self.log.debug("no pricing data")

    async def _get_document_list(self, params: dict):
        request_data = {
            "ndc": params["ndc"],
            "hicl": params["hicl"],
            "gcn": params["gcn"],
            "specificTherapeuticClassCode": params["specificTherapeuticClassCode"],
            "drugCovered": params["drugCovered"],
            "formularyIndicator": params["formularyIndicator"],
            "priorAuthorizationRequired": params["priorAuthorizationRequired"],
            "drug": params["drug"],
            "stepTherapyRequired": params["stepTherapyRequired"],
        }

        url = "https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/forms"  # noqa
        response = await self.page.request.post(url, data=request_data)
        result = await response.json()
        await self.page.wait_for_timeout(900)

        if self._has_valid_document(result):
            return result["drugForms"]
        else:
            self.log.debug(f"no document data for {params['ndc']}")
            return []

    def _map_seach_result(self, med_entry: dict):
        result = {}

        drug_label = (
            "BASE"
            if (not med_entry["genericNdc"] or med_entry["preferredOverGeneric"] == "ALL")
            else "GENERIC"
        )

        result["ndc"] = med_entry["ndc"] if drug_label == "BASE" else med_entry["genericNdc"]
        result["isPackagedDrug"] = med_entry["isPackagedDrug"]
        result["metricSize"] = med_entry["metricSize"]
        result["units"] = "1" if med_entry["isPackagedDrug"] else med_entry["metricSize"]
        result["frequency"] = self._get_frequency_key(med_entry["frequencyOfUse"])
        result["isMultiSourceDrug"] = med_entry["isMultiSourceDrug"]
        result["drugTypeLabel"] = drug_label

        # Parameters used by Documents Listing API call <TricareFormularyApiDocumentsList>
        result["hicl"] = med_entry["hicl"]
        result["gcn"] = med_entry["gcn"]
        result["specificTherapeuticClassCode"] = med_entry["specificTherapeuticClassCode"]

        # To be used for Logging
        result["search_token"] = med_entry["search_token"]
        result["drug_name"] = med_entry["fullName"]
        return result

    def _map_pricing_result(self, mail_price: dict, retail_price: dict):
        result = {}

        result["ndc"] = mail_price["ndc"] if mail_price else retail_price["ndc"]
        result["drugCovered"] = (
            (mail_price["ninetyDays"] and mail_price["ninetyDays"]["drugCovered"])
            or (mail_price["thirtyDays"] and mail_price["thirtyDays"]["drugCovered"])
            or (retail_price["ninetyDays"] and retail_price["ninetyDays"]["drugCovered"])
            or (retail_price["thirtyDays"] and retail_price["thirtyDays"]["drugCovered"])
        )

        result["formularyIndicator"] = (
            mail_price["formularyIndicator"]
            if mail_price["formularyIndicator"] == "t"
            else retail_price["formularyIndicator"]
        )

        result["priorAuthorizationRequired"] = (
            (
                mail_price["ninetyDays"]
                and mail_price["ninetyDays"]["coverage"]["isPriorAuthorizationRequired"]
            )
            or (
                mail_price["thirtyDays"]
                and mail_price["thirtyDays"]["coverage"]["isPriorAuthorizationRequired"]
            )
            or (
                retail_price["ninetyDays"]
                and retail_price["ninetyDays"]["coverage"]["isPriorAuthorizationRequired"]
            )
            or (
                retail_price["thirtyDays"]
                and retail_price["thirtyDays"]["coverage"]["isPriorAuthorizationRequired"]
            )
        )

        # Logic for this value "drug" was not identified in the Site JS Code.
        #  As it does not seems to be the required input. So, sending the value
        # commonly used in the payload on site.

        result["drug"] = None

        result["stepTherapyRequired"] = (
            mail_price
            and mail_price["ninetyDays"]
            and mail_price["ninetyDays"]["coverage"]
            and mail_price["ninetyDays"]["coverage"]["isStepTherapyRequired"]
            and retail_price
            and retail_price["thirtyDays"]
            and retail_price["thirtyDays"]["coverage"]
            and retail_price["thirtyDays"]["coverage"]["isStepTherapyRequired"]
        )

        return result

    def _has_valid_pricing(self, result: dict):
        return (
            result
            and result["mailPricing"]
            and result["retailPricings"]
            and len(result["retailPricings"]) > 0
        )

    def _has_valid_document(self, result: dict):
        return result and result["ndc"] and result["drugForms"] and len(result["drugForms"]) > 0

    def _get_frequency_key(self, frequency: str) -> str:

        """
        Retrieve appropriate frequency value for the textual representation of frequency
        frequencies list is taken from then JS code on "https://www.express-scripts.com/"
        """

        frequencies = [
            {"value": "Daily", "key": "01"},
            {"value": "Every other day", "key": "02"},
            {"value": "Weekly", "key": "07"},
            {"value": "Monthly", "key": "30"},
            {"value": "Every 3 months", "key": "90"},
            {"value": "Yearly", "key": "365"},
        ]

        frequency_key = next(
            iter([item["key"] for item in frequencies if item["value"] == frequency]), frequency
        )
        return frequency_key
