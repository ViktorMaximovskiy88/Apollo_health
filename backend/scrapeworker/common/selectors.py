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
        selectors.append(f'a[href^="javascript:"]')

    if webform:
        selectors.append(f'a[href^="javascript:__doPostBack"]')

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

    [
        selectors.append(f'input[type="hidden"][value$=".{extension}"]')
        for extension in extensions
    ]

    [
        selectors.append(f'input[type="hidden"][value*="{url_keyword}"]')
        for url_keyword in url_keywords
    ]

    return selectors
