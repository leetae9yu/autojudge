#!/usr/bin/env python3
"""
Precedent Data Collection Script

Collects Korean Supreme Court precedents from the Law.go.kr Open API.
Uses environment variable LAW_API_KEY for authentication.

IMPORTANT: Only collects precedents up to 2024-12-31 (2025 is reserved for test set).
Filter: Supreme Court only (대법원)

Usage:
    python collect_precedents.py --keyword "손핵배상" --limit 10
    python collect_precedents.py --keyword "계약" --limit 5 --output-dir ./data/raw/precedents
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError


LAW_API_BASE = "https://www.law.go.kr/DRF"
MAX_DATE = "20241231"  # Only collect up to end of 2024 (2025 reserved for test set)
COURT_FILTER = "대법원"  # Only Supreme Court precedents


def get_api_key() -> str:
    """Get API key from environment variable."""
    api_key = os.environ.get("LAW_API_KEY")
    if not api_key:
        print("Error: LAW_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please set it with: export LAW_API_KEY=your_key", file=sys.stderr)
        sys.exit(1)
    return api_key


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch URL content with error handling."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        raise


def search_precedents(
    query: str,
    api_key: str,
    display: int = 20,
    page: int = 1,
    court: str = COURT_FILTER,
    from_date: str | None = None,
    to_date: str = MAX_DATE,
) -> dict[str, Any]:
    """Search for precedents using the Law.go.kr API."""
    params: dict[str, str] = {
        "OC": api_key,
        "type": "XML",
        "target": "prec",
        "query": query,
        "display": str(display),
        "page": str(page),
    }
    
    if court:
        params["curt"] = court  # Note: API uses 'curt' not 'court'
    
    url = f"{LAW_API_BASE}/lawSearch.do?{urlencode(params)}"
    
    xml_text = fetch_url(url)
    result = parse_precedent_search_xml(xml_text)
    
    # Client-side date filtering to ensure we only get <= 2024
    filtered_items = []
    for item in result["items"]:
        date_str = item.get("선고일자", "").replace(".", "").replace("-", "").replace(" ", "")
        if date_str and len(date_str) >= 8:
            # Check if date is <= 2024-12-31
            if date_str <= MAX_DATE:
                filtered_items.append(item)
        else:
            # If no date, include it (conservative approach)
            filtered_items.append(item)
    
    result["items"] = filtered_items
    result["total_count"] = len(filtered_items)
    
    return result


def parse_precedent_search_xml(xml_text: str) -> dict[str, Any]:
    """Parse precedent search XML response."""
    root = ET.fromstring(xml_text)
    
    items = []
    for prec_elem in root.findall(".//prec"):
        prec_data = {
            "판례일련번호": get_text(prec_elem, "판례일련번호"),
            "사걸명": get_text(prec_elem, "사걸명"),
            "사걸번호": get_text(prec_elem, "사걸번호"),
            "법원명": get_text(prec_elem, "법원명"),
            "선고일자": get_text(prec_elem, "선고일자"),
            "판결유형": get_text(prec_elem, "판결유형"),
            "판례상세링크": get_text(prec_elem, "판례상세링크"),
        }
        items.append(prec_data)
    
    return {
        "total_count": len(items),
        "items": items,
    }


def get_precedent_text(prec_id: str, api_key: str) -> dict[str, Any]:
    """Get detailed precedent text using precedent ID."""
    params = {
        "target": "prec",
        "OC": api_key,
        "type": "JSON",
        "ID": prec_id,
    }
    
    url = f"{LAW_API_BASE}/lawService.do?{urlencode(params)}"
    
    json_text = fetch_url(url)
    return json.loads(json_text)


def get_text(element: ET.Element, tag: str, default: str = "") -> str:
    """Safely get text from XML element."""
    elem = element.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return default


def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing invalid characters."""
    sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
    sanitized = sanitized.strip()
    return sanitized


def save_precedent_to_json(prec_data: dict[str, Any], output_dir: Path) -> Path:
    """Save precedent data to JSON file."""
    case_name = prec_data.get("summary", {}).get("사걸명", "unknown")
    prec_id = prec_data.get("summary", {}).get("판례일련번호", "unknown")
    
    filename = f"{sanitize_filename(case_name)}_{prec_id}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(prec_data, f, ensure_ascii=False, indent=2)
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Collect Korean Supreme Court precedents from Law.go.kr Open API",
        epilog=f"""
Important Notes:
  - Only collects precedents up to 2024-12-31 (2025 reserved for test set)
  - Only collects Supreme Court (대법원) precedents
  - Uses LAW_API_KEY environment variable for authentication
        """,
    )
    parser.add_argument(
        "--keyword",
        required=True,
        help="Search keyword for precedents (e.g., '손핵배상', '계약')",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of precedents to collect (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw/precedents",
        help="Output directory for JSON files (default: data/raw/precedents)",
    )
    parser.add_argument(
        "--fetch-details",
        action="store_true",
        help="Fetch detailed precedent text for each result",
    )
    parser.add_argument(
        "--court",
        type=str,
        default=COURT_FILTER,
        help=f"Court filter (default: {COURT_FILTER})",
    )
    
    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get API key
    api_key = get_api_key()
    
    print(f"Searching for precedents with keyword: '{args.keyword}'")
    print(f"Limit: {args.limit}")
    print(f"Court filter: {args.court}")
    print(f"Max date: {MAX_DATE[:4]}-{MAX_DATE[4:6]}-{MAX_DATE[6:]} (2025 excluded)")
    print(f"Output directory: {output_dir}")
    
    # Search for precedents
    search_result = search_precedents(
        args.keyword,
        api_key,
        display=args.limit,
        court=args.court,
        to_date=MAX_DATE,
    )
    
    if not search_result["items"]:
        print("No precedents found (within date and court filters).")
        return
    
    print(f"Found {search_result['total_count']} precedents (after filtering)")
    
    # Process and save each precedent
    saved_files = []
    excluded_count = 0
    
    for prec_summary in search_result["items"][:args.limit]:
        case_name = prec_summary.get("사걸명", "Unknown")
        prec_id = prec_summary.get("판례일련번호")
        court_name = prec_summary.get("법원명", "Unknown")
        date_str = prec_summary.get("선고일자", "")
        
        # Double-check date filtering
        date_normalized = date_str.replace(".", "").replace("-", "").replace(" ", "")
        if date_normalized and len(date_normalized) >= 8 and date_normalized > MAX_DATE:
            print(f"\nSkipping (2025+): {case_name} - {date_str}")
            excluded_count += 1
            continue
        
        print(f"\nProcessing: {case_name}")
        print(f"  Court: {court_name} | Date: {date_str}")
        
        prec_data = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "search_keyword": args.keyword,
                "date_filter": f"<= {MAX_DATE}",
                "court_filter": args.court,
            },
            "summary": prec_summary,
        }
        
        # Fetch detailed text if requested
        if args.fetch_details and prec_id:
            try:
                print(f"  Fetching detailed text...")
                details = get_precedent_text(prec_id, api_key)
                prec_data["detail"] = details
            except Exception as e:
                print(f"  Warning: Could not fetch details: {e}")
        
        # Save to file
        filepath = save_precedent_to_json(prec_data, output_dir)
        saved_files.append(filepath)
        print(f"  Saved: {filepath.name}")
    
    print(f"\n{'='*50}")
    print(f"Completed! Saved {len(saved_files)} precedent files to {output_dir}")
    if excluded_count > 0:
        print(f"Excluded {excluded_count} files (2025+ dates)")


if __name__ == "__main__":
    main()
