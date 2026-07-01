import re
import logging
from datetime import date
from typing import List, Dict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Fallback splitter for sections that exceed MAX_CHUNK_SIZE
_fallback_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],
)

MAX_CHUNK_SIZE = 500


def _extract_section(content: str, start_pattern: str, end_pattern: str,
                     flags: int = 0) -> str:
    """
    Extracts text between a start and end regex pattern.
    Returns the matched text or an empty string.
    """
    start_match = re.search(start_pattern, content, flags)
    if not start_match:
        return ""

    start_idx = start_match.start()
    remaining = content[start_idx:]
    end_match = re.search(end_pattern, remaining[1:], flags)

    if end_match:
        return remaining[:end_match.start() + 1].strip()
    return remaining.strip()


def _extract_fund_overview(content: str) -> str:
    """
    Extracts: annualized returns headline, NAV, AUM, Expense Ratio, Rating, Min SIP.
    Located at the very start of cleaned content, up to "Return calculator".
    """
    match = re.search(r'Return calculator', content)
    if match:
        return content[:match.start()].strip()
    return content[:500].strip()


def _extract_returns(content: str) -> str:
    """
    Extracts: SIP return calculator data (1Y, 3Y, 5Y, 10Y) only.
    Stops before "Holdings" to avoid including the holdings table.
    """
    section = _extract_section(
        content,
        r'Return calculator',
        r'Holdings \('
    )
    return section


def _extract_top_holdings(content: str, max_holdings: int = 10) -> str:
    """
    Extracts only the top N holdings from the holdings table.
    Uses a simple approach: find the positions of the first N percentage values
    and cut the text there.
    """
    holdings_match = re.search(r'Holdings \( (\d+) \)', content)
    if not holdings_match:
        return ""

    total_count = holdings_match.group(1)
    start_idx = holdings_match.end()
    remaining = content[start_idx:]

    # Find where holdings end — "See All" or "Minimum investments"
    end_match = re.search(r'See All|Minimum investments', remaining)
    full_holdings = remaining[:end_match.start()].strip() if end_match else remaining[:2000].strip()

    # Find positions of all percentage values (e.g., "5.36%", "-13.99%")
    pct_positions = [m.end() for m in re.finditer(r'-?[\d.]+%', full_holdings)]

    header = f"Holdings ( {total_count} )"
    if len(pct_positions) >= max_holdings:
        # Cut after the Nth percentage value
        cut_pos = pct_positions[max_holdings - 1]
        top_text = full_holdings[:cut_pos].strip()
        return f"{header} — Top {max_holdings} of {total_count}: {top_text}"
    elif pct_positions:
        return f"{header}: {full_holdings.strip()}"
    else:
        return f"{header}: {full_holdings[:500]}"


def _extract_min_investments_and_rankings(content: str) -> str:
    """
    Extracts: Minimum investments + Returns and Rankings table.
    From "Minimum investments" or "See All" up to the first "Understand terms Expense ratio".
    """
    section = _extract_section(
        content,
        r'(?:See All\s+)?Minimum investments',
        r'Understand terms Expense ratio'
    )
    return section


def _extract_exit_load_and_tax(content: str) -> str:
    """
    Extracts: Exit load rules, stamp duty, and tax implications.
    From "Exit load, stamp duty and tax" (the second, cleaner exit load block)
    up to "Check past data" or "Compare similar funds" or "Fund management".
    """
    # Prefer the summary block "Exit load, stamp duty and tax"
    section = _extract_section(
        content,
        r'Exit load, stamp duty and tax',
        r'Check past data|Compare similar funds|Fund management'
    )
    if section:
        return section

    # Fallback to the broader "Exit Load" section
    return _extract_section(
        content,
        r'Exit [Ll]oad',
        r'Check past data|Compare similar funds|Fund management'
    )


def _extract_fund_manager(content: str) -> str:
    """
    Extracts: Fund manager names, education, and experience.
    """
    section = _extract_section(
        content,
        r'Fund management',
        r'About '
    )
    return section


def _extract_about_and_objective(content: str) -> str:
    """
    Extracts: About fund description + investment objective + benchmark.
    """
    section = _extract_section(
        content,
        r'About ',
        r'Fund house '
    )
    return section


def _extract_fund_house_info(content: str) -> str:
    """
    Extracts: Fund house, address, custodian, registrar details.
    """
    section = _extract_section(
        content,
        r'Fund house ',
        r'$'  # Take until end of content
    )
    return section


# Ordered list of (section_name, extractor_function)
SECTION_EXTRACTORS = [
    ("Fund Overview", _extract_fund_overview),
    ("Returns", _extract_returns),
    ("Top Holdings", _extract_top_holdings),
    ("Min Investments & Rankings", _extract_min_investments_and_rankings),
    ("Exit Load & Tax", _extract_exit_load_and_tax),
    ("Fund Manager", _extract_fund_manager),
    ("About & Objective", _extract_about_and_objective),
    ("Fund House Info", _extract_fund_house_info),
]


def chunk_fund_content(fund_data: Dict[str, str]) -> List[Document]:
    """
    Takes a single fund's scraped data dict (with 'url', 'fund_name', 'content')
    and produces a list of LangChain Document objects using section-aware chunking.

    Each chunk is prepended with the fund name for retrieval context.
    """
    fund_name = fund_data["fund_name"]
    url = fund_data["url"]
    content = fund_data["content"]
    today = date.today().isoformat()

    documents = []
    chunk_index = 0

    for section_name, extractor in SECTION_EXTRACTORS:
        section_text = extractor(content)
        if not section_text:
            logger.warning(f"[{fund_name}] Section '{section_name}' not found, skipping.")
            continue

        # Prepend fund name to the section text for retrieval context
        prefixed_text = f"{fund_name} — {section_name}: {section_text}"

        # If the section fits in one chunk, use it directly
        if len(prefixed_text) <= MAX_CHUNK_SIZE:
            doc = Document(
                page_content=prefixed_text,
                metadata={
                    "source_url": url,
                    "fund_name": fund_name,
                    "section": section_name,
                    "last_updated": today,
                    "chunk_index": chunk_index,
                }
            )
            documents.append(doc)
            chunk_index += 1
        else:
            # Use RecursiveCharacterTextSplitter as fallback for large sections
            sub_chunks = _fallback_splitter.split_text(prefixed_text)
            for sub_chunk in sub_chunks:
                doc = Document(
                    page_content=sub_chunk,
                    metadata={
                        "source_url": url,
                        "fund_name": fund_name,
                        "section": section_name,
                        "last_updated": today,
                        "chunk_index": chunk_index,
                    }
                )
                documents.append(doc)
                chunk_index += 1

    logger.info(f"[{fund_name}] Created {len(documents)} chunks from {len(SECTION_EXTRACTORS)} sections.")
    return documents


def chunk_all_funds(scraped_data: List[Dict[str, str]]) -> List[Document]:
    """
    Takes the full scraped dataset and produces chunked Documents for all funds.
    """
    all_documents = []
    for fund_data in scraped_data:
        docs = chunk_fund_content(fund_data)
        all_documents.extend(docs)

    logger.info(f"Total chunks created: {len(all_documents)} from {len(scraped_data)} funds.")
    return all_documents


if __name__ == "__main__":
    import json
    import sys

    # Fix encoding for Windows console
    sys.stdout.reconfigure(encoding='utf-8')

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load scraped data
    import os
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_file = os.path.join(PROJECT_ROOT, 'data', 'raw_scraped_data.json')

    with open(data_file, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)

    # Chunk all funds
    documents = chunk_all_funds(scraped_data)

    # Print summary
    print(f"\n{'='*80}")
    print(f"CHUNKING SUMMARY")
    print(f"{'='*80}")
    for doc in documents:
        meta = doc.metadata
        preview = doc.page_content[:100].replace('\n', ' ')
        print(f"  [{meta['chunk_index']:2d}] {meta['fund_name'][:40]:<40} | "
              f"{meta['section']:<25} | {len(doc.page_content):4d} chars | {preview}...")
    print(f"\nTotal: {len(documents)} chunks")
