from backend.parseworker.extractors.basic_table_extractor import BasicTableExtraction


class UHCFormularyExtraction(BasicTableExtraction):
    def skip_table(self, table: list[list[str]]):
        cell = table[0][0]
        return cell == "$" or \
            cell == "Drug Tier" or \
            cell is None