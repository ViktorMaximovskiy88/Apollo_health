from backend.common.models.site import AttrSelector


def filter_by_href(
    extensions=[],
    keywords=[],
    url_keywords=[],
    javascript=False,
    webform=False,
):
    ###
    # Generate CSS selectors for anchor tags
    ###
    selectors = []

    if javascript:
        selectors.append('a[href^="javascript:"]')

    if webform:
        selectors.append('a[href^="javascript:__doPostBack"]')

    [selectors.append(f'a[href$=".{extension}"]') for extension in extensions]
    [selectors.append(f'a[href*="{url_keyword}"]') for url_keyword in url_keywords]
    [selectors.append(f'a:has-text("{keyword}")') for keyword in keywords]

    return selectors


def filter_by_hidden_value(
    extensions=[],
    url_keywords=[],
):
    ###
    # Generate CSS selectors for hidden input
    ###

    selectors = []

    [selectors.append(f'input[type="hidden"][value$=".{extension}"]') for extension in extensions]

    [
        selectors.append(f'input[type="hidden"][value*="{url_keyword}"]')
        for url_keyword in url_keywords
    ]

    return selectors


def to_xpath(attr_selector: AttrSelector) -> str:
    ###
    # Convert AttrSelector to xpath string
    ###
    base_selector = f'@*[contains(name(), "{attr_selector.attr_name}")]'
    selector = base_selector
    if attr_selector.attr_value:
        selector = f'contains({base_selector}, "{attr_selector.attr_value}")'
    if attr_selector.has_text:
        selector = f'{selector} and contains(text(), "{attr_selector.has_text}")'
    return f"//a[{selector}]"
