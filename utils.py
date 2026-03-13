import re
from config import log

def clean_text(text: str | None) -> str:
    """Collapse whitespace and strip a string."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def build_page_url(page_num: int, base_url: str) -> str:
    """Return the listing URL for a given page number."""
    if page_num <= 1:
        return base_url
    return f"{base_url}?page={page_num}"

async def dismiss_overlays(page): # Not sure whether we need this or not, but just in case
    """Try to close any cookie consent banners or overlays that block clicks."""
    dismiss_selectors = [
        'button[data-automation="dismiss"]',
        'button:has-text("ยอมรับ")',
        'button:has-text("Accept")',
        'button:has-text("ตกลง")',
        '[aria-label="close"]',
        '[aria-label="Close"]',
        'button:has-text("Close")',
        '.cookie-banner button',
        '#onetrust-accept-btn-handler',
    ]
    for sel in dismiss_selectors:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=1_000):
                await btn.click()
                log.info(f"Dismissed overlay via: {sel}")
                await page.wait_for_timeout(500)
        except Exception:
            pass
