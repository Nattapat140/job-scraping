from config import BASE_URL, JOBS_PER_PAGE, TIMEOUT, NAV_TIMEOUT, log
from utils import clean_text, build_page_url, dismiss_overlays
from playwright.async_api import TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Core scraping logic
# ---------------------------------------------------------------------------
async def extract_job_details(page, job_url: str) -> dict:
    """
    Extract structured data from a full job detail page.
    The page should already be navigated to the job URL.
    """
    # Wait for the main container
    try:
        await page.wait_for_selector(
            '[data-automation="jobDetailsPage"]',
            state="visible",
            timeout=TIMEOUT,
        )
    except PlaywrightTimeout:
        log.warning("Job detail page container not found – skipping.")
        return {}

    # --- Structured fields ---------------------------------------------------
    async def safe_text(selector: str) -> str:
        try:
            el = page.locator(selector).first
            await el.wait_for(state="attached", timeout=4_000)
            return clean_text(await el.inner_text())
        except Exception:
            return ""

    title = await safe_text('[data-automation="job-detail-title"]')
    if not title:
        title = await safe_text("h1")

    company = await safe_text('[data-automation="advertiser-name"]')
    location = await safe_text('[data-automation="job-detail-location"]')
    salary = await safe_text('[data-automation="job-detail-salary"]')
    work_type = await safe_text('[data-automation="job-detail-work-type"]')

    # Posted date – try multiple selectors
    posted_date = await safe_text('[data-automation="job-detail-date"]')
    if not posted_date:
        posted_date = await safe_text('[data-automation="jobListingDate"]')

    # --- Full job description (HTML → plain text) ----------------------------
    description = ""
    try:
        desc_el = page.locator('[data-automation="jobAdDetails"]').first
        await desc_el.wait_for(state="attached", timeout=4_000)
        description = clean_text(await desc_el.inner_text())
    except Exception:
        pass

    return {
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "work_type": work_type,
        "posted_date": posted_date,
        "description": description,
        "job_url": job_url,
    }

async def collect_job_urls(page) -> list[str]:
    """Collect all job link hrefs from the current listing page."""
    job_links = page.locator('[data-automation="job-list-view-job-link"]')
    count = await job_links.count()
    urls = []
    for i in range(min(count, JOBS_PER_PAGE)):
        try:
            href = await job_links.nth(i).get_attribute("href")
            if href:
                if not href.startswith("http"):
                    href = f"https://th.jobsdb.com{href}"
                urls.append(href)
        except Exception:
            pass
    return urls

async def scrape_page(page, page_num: int) -> list[dict]:
    """Scrape all job listings on a single page."""
    listing_url = build_page_url(page_num, BASE_URL)
    log.info(f"Navigating to page {page_num}: {listing_url}")
    await page.goto(listing_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

    # Wait for job links to appear
    await page.wait_for_selector(
        '[data-automation="job-list-view-job-link"]',
        state="attached",
        timeout=TIMEOUT,
    )
    # Wait for SPA hydration
    await page.wait_for_timeout(3_000)

    # Dismiss any cookie banners / overlays
    await dismiss_overlays(page)

    # Collect all job URLs from the listing
    job_urls = await collect_job_urls(page)
    log.info(f"Found {len(job_urls)} job links on page {page_num}")

    page_results: list[dict] = []

    for idx, job_url in enumerate(job_urls):
        log.info(f"  [{page_num}-{idx+1}/{len(job_urls)}] Visiting: {job_url[:80]}...")
        try:
            # Navigate to the full job detail page
            await page.goto(job_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
            await page.wait_for_timeout(1_500)

            # Extract details
            data = await extract_job_details(page, job_url)
            if data and data.get("title"):
                data["page_number"] = page_num
                data["index_on_page"] = idx + 1
                page_results.append(data)
                log.info(f"    ✓ {data['title']} @ {data['company']}")
            else:
                log.warning(f"    ✗ Could not extract details for job #{idx+1}")

        except PlaywrightTimeout:
            log.warning(f"    ✗ Timeout on job #{idx+1} – skipping.")
        except Exception as e:
            log.warning(f"    ✗ Error on job #{idx+1}: {e}")

    return page_results

async def has_next_page(page) -> bool:
    """Check whether a 'Next' pagination button exists and is enabled."""
    try:
        # Thai label: "ถัดไป"
        next_btn = page.locator('a[aria-label="ถัดไป"]')
        if await next_btn.count() > 0:
            is_disabled = await next_btn.get_attribute("aria-disabled")
            return is_disabled != "true"
    except Exception:
        pass
    return False