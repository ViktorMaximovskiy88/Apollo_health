from backend.common.core.enums import ScrapeMethod
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class TricareScraper(PlaywrightBaseScraper):

    type: str = "Tricare"
    downloads: list[DownloadContext] = []

    def css_selector(self) -> str:
        return ""

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.scrape_method == ScrapeMethod.Tricare
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        timeout = self.config.wait_for_timeout_ms
        tricare_url = "https://www.express-scripts.com/frontend/open-enrollment/tricare/fst/#/"
        # TODO need to get these terms added to somewhere....
        search_terms = ["adipex", "simvastatin", "zocor"]

        await self.page.goto(tricare_url)
        await self.page.locator("#formularySearchDefault").wait_for(timeout=timeout)

        # # step 1: get search term data from typeahead
        search_results = await self._search_for_terms(search_terms)

        # step 2: get search results from price API
        for search_params in search_results:
            pricing_result = await self._get_search_term_pricing(search_params)
            if pricing_result:
                pricing_result["ndc"] = search_params["ndc"]
                pricing_result["hicl"] = search_params["hicl"]
                pricing_result["gcn"] = search_params["gcn"]
                pricing_result["specificTherapeuticClassCode"] = search_params[
                    "specificTherapeuticClassCode"
                ]

                # TODO refactor...
                # step 3: get content aka docs
                documents = await self._get_document_list(pricing_result)
                for document in documents:
                    name: str = (
                        f"{search_params['search_token']} {document['type']}"  # we have type too
                    )

                    metadata: Metadata = Metadata(
                        link_text=name,
                        base_url=self.page.url,  # self.base_url # 'real one' or tricare?
                    )

                    url = "https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/forms/content"  # noqa
                    url += f"?repository={document['repository']}&documentId={document['documentId']}"  # noqa
                    # TODO look at liams changes for cookies
                    cookies = await self.context.cookies(self.page.url)
                    downloads.append(
                        DownloadContext(
                            metadata=metadata,
                            request=Request(
                                url=url,
                                cookies=cookies,
                            ),
                        )
                    )

        return downloads

    async def _search_for_terms(self, search_terms: list[str]) -> list[dict]:
        results = []
        for search_term in search_terms:
            search_url = f"https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/search?name={search_term}&context=fst"
            response = await self.page.request.get(search_url)
            search_result = await response.json()

            if isinstance(search_result, list) and not len(search_result):
                continue

            for result in search_result:
                existing_data = [item for item in results if item["ndc"] == result["ndc"]]
                if len(existing_data) == 0:
                    result["search_token"] = search_term
                    results.append(result)

        return [self._map_seach_result(result) for result in results]

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
        url = "https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/pricing"
        response = await self.page.request.post(url, data=request_data)
        result = await response.json()

        if self._has_valid_pricing(result):
            return self._map_pricing_result(result["mailPricing"], result["retailPricings"][0])
        else:
            self.log.info("no pricing data")

    async def _get_document_list(self, params: dict):
        # TODO we need to append some of these from the other request...
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
        url = "https://www.express-scripts.com/frontendservice/proxinator/1/member/v1/drugpricing/prelogin/fst/drug/forms"
        response = await self.page.request.post(url, data=request_data)
        result = await response.json()

        if self._has_valid_document(result):
            return result["drugForms"]
        else:
            self.log.info(f"no document data for {params['drug']}")
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
