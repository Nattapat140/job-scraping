# JobsDB Thailand Scraper

Scrapes **ICT Hybrid Full-time** job listings from [JobsDB Thailand](https://th.jobsdb.com/th/jobs-in-information-communication-technology/in-ไทย/full-time/hybrid) using **Playwright** (Python, async).

## How It Works

1. Navigates to the listing page
2. Clicks each job link (`data-automation="job-list-view-job-link"`) one by one (up to 32 per page)
3. Extracts structured data from the detail panel (`data-automation="jobDetailsPage"`)
4. After finishing all jobs on a page, moves to the next page via pagination
5. Saves results to **JSON** and **CSV**

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers (Chromium)
playwright install chromium

# 3. Run the scraper
python main.py
```

## Configuration

Edit the constants at the top of `scraper.py`:

| Variable       | Default | Description                                |
|----------------|---------|--------------------------------------------|
| `HEADLESS`     | `True`  | Set `False` to watch the browser           |
| `SLOW_MO`      | `0`     | Delay (ms) between actions for debugging   |
| `MAX_PAGES`    | `20`    | Max pages to scrape (`None` = all)         |
| `JOBS_PER_PAGE`| `32`    | Max jobs to process per page               |

## Output

Results are saved in the project directory with timestamps:
- `jobsdb_results_YYYYMMDD_HHMMSS.json`
- `jobsdb_results_YYYYMMDD_HHMMSS.csv`

### Fields Extracted

| Field         | Description                          |
|---------------|--------------------------------------|
| `title`       | Job title                            |
| `company`     | Company / advertiser name            |
| `location`    | Job location                         |
| `salary`      | Salary information (if listed)       |
| `work_type`   | Full Time, Hybrid, etc.              |
| `posted_date` | Date the job was posted              |
| `description` | Full job description (plain text)    |
| `job_url`     | Link to the job detail               |
| `page_number` | Which listing page this was found on |
| `index_on_page` | Position on that page (1-32)       |
