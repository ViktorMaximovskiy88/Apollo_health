from playwright.sync_api import Request, Route, sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://apps.humana.com/tad/Tad_New/Search.aspx?sortfield=name&policyType=pharmacy")
    page.once("dialog", lambda dialog: dialog.accept())

    def intercept(route: Route, request: Request):
        print(request.url)
        route.continue_()

    page.route("**/*", intercept)

    for link in page.query_selector_all('a[href^="javascript:__doPostBack"]'):
        id = link.get_attribute("id")
        if id:
            page.locator(f"#{id}").click()
