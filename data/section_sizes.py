"""Quick diagnostic: show section sizes per fund."""
import json, re, os, sys

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
with open(os.path.join(PROJECT_ROOT, 'data', 'raw_scraped_data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

for fund in data:
    name = fund['fund_name']
    c = fund['content']
    print(f"\n{'='*60}")
    print(f"FUND: {name}")
    print(f"Total content: {len(c)} chars")
    
    # Fund Overview: start to "Return calculator"
    m = re.search(r'Return calculator', c)
    overview = c[:m.start()] if m else c[:500]
    print(f"  Fund Overview:    {len(overview):5d} chars")
    
    # Returns: "Return calculator" to "Understand terms Expense ratio"
    s = re.search(r'Return calculator', c)
    e = re.search(r'Understand terms Expense ratio', c)
    returns = c[s.start():e.start()] if s and e else ""
    print(f"  Returns:          {len(returns):5d} chars")
    
    # Holdings: "Holdings (" to "See All" or "Minimum investments"
    s = re.search(r'Holdings \(', c)
    e = re.search(r'See All|Minimum investments', c[s.start():]) if s else None
    holdings = c[s.start():s.start()+e.start()] if s and e else ""
    print(f"  Holdings (raw):   {len(holdings):5d} chars")
    
    # Exit Load: "Exit Load" to "Check past data" or "Compare similar" or "Fund management"
    s = re.search(r'Exit [Ll]oad', c)
    remaining = c[s.start():] if s else ""
    e = re.search(r'Check past data|Compare similar funds|Fund management', remaining[1:])
    exit_load = remaining[:e.start()+1] if e else remaining
    print(f"  Exit Load & Tax:  {len(exit_load):5d} chars")
    
    # Fund Manager
    s = re.search(r'Fund management', c)
    remaining = c[s.start():] if s else ""
    e = re.search(r'About ', remaining[1:])
    fm = remaining[:e.start()+1] if e else remaining
    print(f"  Fund Manager:     {len(fm):5d} chars")
    
    # About & Objective
    s = re.search(r'About ', c)
    remaining = c[s.start():] if s else ""
    e = re.search(r'Fund house ', remaining[1:])
    about = remaining[:e.start()+1] if e else remaining
    print(f"  About & Obj:      {len(about):5d} chars")
    
    # Fund House Info
    s = re.search(r'Fund house ', c)
    fh = c[s.start():] if s else ""
    print(f"  Fund House Info:  {len(fh):5d} chars")
