"""
Script to analyze the structure of the raw scraped data
and recommend a chunking strategy.
"""
import json
import re

with open("data/raw_scraped_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Common Groww site-wide boilerplate patterns
# These appear on every page and are not fund-specific
BOILERPLATE_MARKERS = [
    "Stocks Invest in Stocks Invest in stocks, ETFs, IPOs",
    "Top Gainers Stocks 52 Weeks High Stocks",
    "SIP Calculator Brokerage Calculator RD Calculator",
    "Terms and Conditions Policies and Procedures",
    "Mutual Funds : A B C D E F G H I J K L M N O P Q R S T U V W X Y Z",
    "GROWW About Us Pricing Blog Media",
    "Vaishnavi Tech Park, South Tower",
]

for i, entry in enumerate(data):
    url = entry["url"]
    content = entry["content"]
    
    print(f"\n{'='*80}")
    print(f"URL {i+1}: {url}")
    print(f"Total characters: {len(content)}")
    
    # Try to find where boilerplate starts
    boilerplate_start = len(content)
    for marker in BOILERPLATE_MARKERS:
        idx = content.find(marker)
        if idx != -1 and idx < boilerplate_start:
            boilerplate_start = idx
    
    # Find the fund-specific content start (after initial boilerplate nav)
    # Look for the NAV/return data which signals start of fund content
    nav_patterns = [
        r'\d+Y annualised',
        r'NAV:',
        r'Fund size \(AUM\)',
    ]
    content_start = 0
    for pattern in nav_patterns:
        match = re.search(pattern, content)
        if match:
            # Go back a bit to capture the return percentage
            content_start = max(0, match.start() - 50)
            break
    
    # Find key data sections
    sections_found = []
    section_markers = [
        ("NAV & Returns", r'NAV:.*?₹[\d,.]+'),
        ("Fund Size (AUM)", r'Fund size \(AUM\).*?Cr'),
        ("Expense Ratio", r'Expense ratio [\d.]+%'),
        ("SIP Minimum", r'Min\. for SIP ₹[\d,]+'),
        ("Holdings", r'Holdings \( \d+ \)'),
        ("Exit Load", r'Exit [Ll]oad.*?(?:days|year|months)'),
        ("Tax Implication", r'Tax implication.*?(?:taxed|Check)'),
        ("Fund Manager", r'Fund management.*?(?:Present|View details)'),
        ("About Fund", r'About.*?Fund Direct Growth.*?(?:Investment Objective|Fund benchmark)'),
        ("Investment Objective", r'Investment Objective.*?(?:Fund benchmark|Scheme Information)'),
        ("Fund House Info", r'Fund house.*?(?:Custodian|Registrar)'),
    ]
    
    for name, pattern in section_markers:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sections_found.append((name, match.start(), match.end(), match.end() - match.start()))
    
    print(f"\nSections found:")
    for name, start, end, length in sorted(sections_found, key=lambda x: x[1]):
        print(f"  - {name}: chars {start}-{end} (length: {length})")
    
    # Count holdings-like repetitive data
    holdings_match = re.search(r'Holdings \( (\d+) \)', content)
    if holdings_match:
        print(f"\nHoldings count: {holdings_match.group(1)}")
    
    # Estimate boilerplate vs useful content
    useful_content = content[content_start:boilerplate_start] if content_start < boilerplate_start else content
    print(f"\nEstimated useful content: {len(useful_content)} chars ({len(useful_content)*100//len(content)}% of total)")
    print(f"Estimated boilerplate: {len(content) - len(useful_content)} chars")
    
    # Show a snippet of the useful content start
    print(f"\nUseful content starts with:")
    print(f"  '{useful_content[:200]}...'")
    
    # Show where useful content ends
    print(f"\nUseful content ends with:")
    print(f"  '...{useful_content[-200:]}'")
