"""
JobsDB Thailand - ICT Hybrid Full-time Job Scraper
Uses Playwright (async) to scrape JS-rendered job listings.
"""

import asyncio
import gc
from config import BASE_URL, MAX_PAGES, HEADLESS, SLOW_MO, NAV_TIMEOUT, CSV_PATH, log
from utils import build_page_url
from csv_helper import init_csv, append_to_csv
from scrape import scrape_page, has_next_page
from playwright.async_api import async_playwright

async def main():
    log.info("JobsDB Thailand Scraper – Starting")
    log.info("=" * 67)

    # Initialise CSV (create or resume)
    total_rows = init_csv()
    log.info(f"Starting from row index: {total_rows}")

    page_num = 1

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="th-TH",
        )
        page = await context.new_page()

        while True:
            if MAX_PAGES and page_num > MAX_PAGES:
                log.info(f"Reached MAX_PAGES cap ({MAX_PAGES}). Stopping.")
                break

            # ------ Scrape one page ------
            try:
                page_results = await scrape_page(page, page_num)
            except Exception as e:
                log.error(f"Failed to scrape page {page_num}: {e}")
                break

            # ------ Write this page's results to CSV immediately ------
            written = append_to_csv(page_results)
            total_rows += written
            log.info(
                f"Page {page_num} done – {written} jobs written to CSV "
                f"(total rows in CSV: {total_rows})"
            )

            # ------ Clear page data from memory ------
            page_results.clear()
            del page_results
            gc.collect()
            log.info(f"Memory cleared after page {page_num}")

            # ------ Go back to listing to check pagination ------
            listing_url = build_page_url(page_num, BASE_URL)
            await page.goto(
                listing_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT
            )
            await page.wait_for_timeout(2_000)

            if await has_next_page(page):
                page_num += 1
            else:
                log.info("No more pages – finished.")
                break

        await browser.close()

    log.info("=" * 67)
    log.info(f"DONE – Total jobs scraped: {total_rows}")
    log.info(f"CSV saved at: {CSV_PATH}")
    log.info("=" * 67)

if __name__ == "__main__":
    asyncio.run(main())
