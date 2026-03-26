import os
import logging
from datetime import datetime

# ---------------------------
# Directory & File Paths
# ---------------------------
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_PATH = os.path.join(OUTPUT_DIR, f"jobsdb_results_{TIMESTAMP}.csv")

# ---------------------------
# Scraping Configuration
# ---------------------------
BASE_URL = "https://th.jobsdb.com/th/jobs-in-information-communication-technology/full-time"
JOBS_PER_PAGE = 32
MAX_PAGES = None
HEADLESS = True
SLOW_MO = 0
TIMEOUT = 20_000
NAV_TIMEOUT = 80_000

# ---------------------------
# CSV Metadata
# ---------------------------
CSV_FIELDS = [
    "title", "company", "location", "salary", "work_type",
    "posted_date", "description", "job_url", "page_number", "index_on_page",
]

# ---------------------------
# Logging Setup
# ---------------------------
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("jobsdb")

log = setup_logging()
