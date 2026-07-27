from playwright.sync_api import sync_playwright
import json


AIRTABLE_URL = (
    "https://airtable.com/appsseXTOVx59HC0W/pagcVengefPFQvMZC/form"
)


def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()


        # Capture Airtable dropdown API response
        def handle_response(response):
            if "listRowsMatchingNameAndFilters" in response.url:
                print("\n========== AIRTABLE RESPONSE ==========")
                print(response.url)

                try:
                    data = response.json()
                    print(json.dumps(data, indent=2))

                except Exception:
                    print(response.text())


        page.on("response", handle_response)


        print("Opening Airtable...")
        
        page.goto(
            AIRTABLE_URL,
            wait_until="networkidle"
        )

        print("Page loaded")


        # Automatically open Add Unit dropdown
        try:
            page.get_by_text("Add unit").click()
            print("Clicked Add unit")

        except Exception as e:
            print("Could not click Add unit:")
            print(e)


        # Keep browser alive long enough to capture response
        page.wait_for_timeout(10000)


        browser.close()


if __name__ == "__main__":
    main()