import os
from playwright.sync_api import sync_playwright

# Retrieve your ZenRows API key
API_KEY = os.environ.get("ZENROWS_API_KEY")

# Construct the remote browser WebSocket endpoint provided by ZenRows
connection_url = f"wss://browser.zenrows.com?apikey={API_KEY}"

with sync_playwright() as p:
    # Connect to ZenRows remote browser infrastructure instead of a local browser
    browser = p.chromium.connect_over_cdp(connection_url)
    page = browser.new_page()

    try:
        print("Navigating to target page through Zenrows Browser Session...")
        page.goto("https://www.scrapingcourse.com/ecommerce/", wait_until="domcontentloaded")

        # 1. Perform multi-step interaction (e.g., waiting for elements, clicking)
        print("Waiting for products to load...")
        page.locator(".product").first.wait_for()

        # 2. Extract structured data or run custom JS within the live session
        title = page.title()
        product_count = page.locator(".product").count()
        print(f"Page Title: {title}")
        print(f"Found {product_count} products on the page.")

        # Example of a click interaction if required by your workflow:
        # page.locator("text=Next Page").click()

    finally:
        # Always close the remote session cleanly
        browser.close()
