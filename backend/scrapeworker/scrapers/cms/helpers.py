from datetime import datetime
from itertools import groupby

from lxml import etree
from pandas import DataFrame


def to_date_string(string_date: str) -> str:
    """
    Convert a string date into specific m/d/y format string date
    :param string_date: string date
    :return: m/d/y string date
    """
    parsed_date = datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S")
    return str(parsed_date.strftime("%m/%d/%Y"))


def group_table_by(table_template: str) -> str:
    """
    Group HTML tables rows by CODE column for LCD and LCA documents
    :param table_template: input HTML table as string
    :return: grouped HTML table as string
    """
    html_document = etree.fromstring(table_template.replace("&", "&amp;"), None)
    all_codes = [row.xpath(".//td")[0].text for row in html_document.xpath("//tbody/tr")]
    grouped_list = [item[0] for item in list(groupby(sorted(all_codes), lambda x: x[0:2]))]
    for item in grouped_list:
        founds_rows = [code for code in all_codes if code.startswith(item)]
        if len(founds_rows) > 1:
            # remove all table rows except first one
            for row_to_remove in founds_rows[1:]:
                row_to_remove_node = html_document.xpath(f'//tr/td[text()="{row_to_remove}"]')[0]
                row_to_remove_node.getparent().getparent().remove(row_to_remove_node.getparent())
            # fix first element
            first_item = html_document.xpath(f'//tr/td[text()="{founds_rows[0]}"]')[0]
            first_item.text = f"0{first_item.text[0:2]}X"
        else:
            first_item = html_document.xpath(f'//tr/td[text()="{founds_rows[0]}"]')[0]
            if len(first_item.text) == 2:
                first_item.text = f"0{first_item.text}x"
            elif len(first_item.text) == 3:
                first_item.text = f"0{first_item.text}"
    table_template = etree.tostring(html_document).decode("utf-8")
    return table_template


def search_data_frame(
    data_source: DataFrame,
    search_params: list[str],
    search_values,
    as_data_frame=False,
    operator="&",
):
    """
    Perform a search within pandas DataFrame by the set of parameters and values
    :param data_source: source DataFrame
    :param search_params: an array of parameters to search
    :param search_values:an array of values to search
    :param as_data_frame: optional flag to retrieve results as a DataFrame
    :param operator: optional search logic operator accepts '&' or '|'
    :return: List of records or a new DataFrame if as_data_frame is set to True
    """
    if len(search_params) < len(search_values):
        while len(search_params) != len(search_values):
            search_params.append(search_params[0])
    conditions = []
    x = 0
    while x < len(search_params):
        conditions.append(f"{search_params[x]} == {search_values[x]}")
        x += 1
    if as_data_frame:
        return data_source.query(f" {operator} ".join(conditions))
    else:
        return data_source.query(f" {operator} ".join(conditions)).to_dict("records")


def greater_than_today(string_date: str) -> bool:
    """
    Check if the provided date is greater than today
    :param string_date: date as string
    :return: True if greater, False if not greater or the input value is None
    """
    if string_date is None:
        return False
    return datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S") > datetime.now()
