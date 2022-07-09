import re
from backend.parseworker.extractors.basic_table_extractor import BasicTableExtraction


class MedigoldFormularyExtraction(BasicTableExtraction):
    def skip_table(self, table):
        cell = table[0][0]
        return "PA - Prior Authorization" in cell

    def clean_table(self, table: list[list[str]]):
        header = table[0]
        clean_table = [header]
        for row in table[1:]:
            if row[0]: continue
            if row[1] == None: continue

            for i, cell in enumerate(row):
                row[i] = re.sub(r"\s+", ' ', str(cell))

            if row[2] == '':
                clean_table[-1][1] += f' {row[1]}'
            else:
                clean_table.append(row)

        return clean_table
