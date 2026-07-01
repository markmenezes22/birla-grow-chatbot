import requests
from bs4 import BeautifulSoup
import logging
import json
import os
import re
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root directory (two levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_FILE = os.path.join(RAW_DATA_DIR, 'raw_scraped_data.json')

GROWW_URLS = [
    "https://groww.in/mutual-funds/birla-sun-life-cash-plus-direct-growth",
    "https://groww.in/mutual-funds/birla-sun-life-new-millennium-direct-growth",
    "https://groww.in/mutual-funds/aditya-birla-sun-life-large-cap-direct-fund-growth",
    "https://groww.in/mutual-funds/aditya-birla-sun-life-nifty-midcap-150-index-fund-direct-growth",
    "https://groww.in/mutual-funds/birla-sun-life-small-midcap-fund-direct-growth"
]


def _extract_fund_name(content: str) -> str:
    """
    Extracts the fund name from the page title at the beginning of the content.
    e.g. "Aditya Birla Sun Life Liquid Fund Direct Growth"
    """
    match = re.match(r'^(.*?)\s*-\s*NAV', content)
    if match:
        return match.group(1).strip()
    return ""


def _strip_boilerplate(content: str) -> str:
    """
    Strips Groww site-wide boilerplate from the scraped content:
    1. Removes the navigation menu at the start (~1,900 chars of Groww platform links).
    2. Removes the footer (stock tickers, calculators, links) after the fund house info.
    """
    # --- Strip leading navigation boilerplate ---
    # The fund-specific content starts at the annualized return line.
    # Pattern: "+X.XX % 3Y annualised" (the first fund metric on every page)
    start_match = re.search(r'[+-][\d.]+ % \dY annualised', content)
    if start_match:
        content_start = start_match.start()
    else:
        # Fallback: look for "NAV:" which is always present
        nav_match = re.search(r'NAV:', content)
        content_start = nav_match.start() if nav_match else 0

    # --- Strip trailing footer boilerplate ---
    # The footer starts after the Registrar & Transfer Agent address.
    # Reliable marker: "Home > Mutual Funds >" breadcrumb that appears after the
    # registrar address and before the Groww footer.
    end_match = re.search(r'Home\s*>\s*Mutual Funds\s*>', content)
    if end_match:
        content_end = end_match.start()
    else:
        # Fallback: look for the Groww footer marker
        footer_match = re.search(r'GROWW About Us Pricing', content)
        content_end = footer_match.start() if footer_match else len(content)

    stripped = content[content_start:content_end].strip()
    return stripped


def scrape_url(url: str) -> str:
    """
    Fetches the HTML content of a URL and extracts the main text,
    removing navbars, footers, scripts, etc.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Remove script, style, header, footer, nav, and other non-content elements
    for element in soup(["script", "style", "header", "footer", "nav", "noscript", "svg", "button", "iframe"]):
        element.extract()
        
    # Extract text with space separation
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up multiple spaces
    cleaned_text = ' '.join(text.split())
    
    return cleaned_text


def scrape_all_urls(urls: List[str] = GROWW_URLS) -> List[Dict[str, str]]:
    """
    Scrapes a list of URLs and returns a list of dictionaries with
    url, fund_name, and cleaned content (boilerplate stripped).
    """
    scraped_data = []
    for url in urls:
        logger.info(f"Scraping {url}...")
        raw_content = scrape_url(url)
        if raw_content:
            fund_name = _extract_fund_name(raw_content)
            cleaned_content = _strip_boilerplate(raw_content)
            scraped_data.append({
                "url": url,
                "fund_name": fund_name,
                "content": cleaned_content
            })
            logger.info(
                f"Extracted '{fund_name}': {len(cleaned_content)} chars "
                f"(stripped from {len(raw_content)} raw chars)"
            )
        else:
            logger.warning(f"No content extracted from {url}")
            
    return scraped_data


def save_raw_data(data: List[Dict[str, str]], filepath: str = RAW_DATA_FILE) -> None:
    """
    Saves the scraped data to a JSON file for inspection and reuse.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Scraped data saved to {filepath}")


if __name__ == "__main__":
    logger.info("Starting Web Scraper...")
    data = scrape_all_urls()
    logger.info(f"Scraped {len(data)} pages successfully out of {len(GROWW_URLS)}.")
    
    # Save data to disk
    save_raw_data(data)
    
    # Print a small snippet of the first scraped page to verify
    if data:
        logger.info(f"Fund: {data[0]['fund_name']}")
        logger.info(f"Snippet: {data[0]['content'][:200]}...")
