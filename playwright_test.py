from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    print("Playwright started!")
    browser = p.chromium.launch(headless=True)
    print("Browser launched!")
    browser.close()