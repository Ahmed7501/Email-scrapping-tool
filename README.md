# Modular Email Scraper Tool

## Features
- Upload a file (CSV, XLSX, DOCX, or TXT) containing URLs
- For each URL:
  - Fully render the page using Selenium (undetected-chromedriver)
  - If no emails found, crawl to /contact, /about, /team, etc.
  - Extract website title, category (meta description), and all emails (visible and mailto)
- Save results in CSV or Excel: `Original URL`, `Scraped URL`, `Title`, `Category`, `Emails`, `Status`
- Proxy support, user-agent rotation, human-like delays
- Modular codebase for easy extension

## Modules
- `file_loader.py`: Handles file input and URL extraction
- `proxy_manager.py`: Manages proxy rotation
- `selenium_scraper.py`: Loads and renders pages, scrolls, waits
- `crawler.py`: Finds internal pages like /contact, /about, /team
- `email_extractor.py`: Extracts emails using regex
- `output_writer.py`: Saves results to CSV/Excel
- `main.py`: Orchestrates the workflow

## Requirements
```
pip install -r requirements.txt
```

## Usage
```sh
python main.py input.xlsx output.csv --output_type csv
# or for Excel output
python main.py input.xlsx output.xlsx --output_type excel
```

## Extending
- Add social media scraping, Streamlit UI, or more advanced crawling as needed.

## Notes
- Requires Chrome and undetected-chromedriver for best results.
- For best anti-bot evasion, use proxies and rotate user-agents. 