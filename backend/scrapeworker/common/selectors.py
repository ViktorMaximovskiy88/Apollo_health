def filter_by_href(
    extensions=[],
    keywords=[],
    javascript=False,
):
    ###
    # Generate CSS selectors for anchor tags
    ###
    selectors = []

    if javascript:
        selectors.append(f'a[href^="javascript:"]')

    [selectors.append(f'a[href$=".{extension}"]') for extension in extensions]
    [selectors.append(f'a[href*="{keyword}"]') for keyword in keywords]

    return selectors


def filter_by_hidden_value(
    extensions=[],
    keywords=[],
):
    ###
    # Generate CSS selectors for hidden input
    ###

    selectors = []

    [selectors.append(
        f'input[type="hidden"][value$=".{extension}"]') for extension in extensions]

    [selectors.append(
        f'input[type="hidden"][value*="{keyword}"]') for keyword in keywords]

    return selectors
