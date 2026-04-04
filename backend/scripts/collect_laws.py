#!/usr/bin/env python3
"""
Law Data Collection Script

Collects Korean law data from the Law.go.kr Open API.
Uses environment variable LAW_API_KEY for authentication.

Usage:
    python collect_laws.py --keyword "민법" --limit 10
    python collect_laws.py --keyword "형법" --limit 5 --output-dir ./data/raw/laws
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


def search_laws(query: str, api_key: str, display: int = 20, page: int = 1) -> dict[str, Any]:
    """Search for laws using the Law.go.kr API."""
    params = {
        "OC": api_key,
        "type": "XML",
        "target": "law",
        "query": query,
        "display": display,
        "page": page,
    }
    url = f"{LAW_API_BASE}/lawSearch.do?{urlencode(params)}"
    
    xml_text = fetch_url(url)
    return parse_law_search_xml(xml_text)


def parse_law_search_xml(xml_text: str) -> dict[str, Any]:
    """Parse law search XML response."""
    root = ET.fromstring(xml_text)
    
    laws = []
    for law_elem in root.findall(".//law"):
        law_data = {
            "법령명한글": get_text(law_elem, "법령명한글"),
            "법령명약칭": get_text(law_elem, "법령명약칭"),
            "법령ID": get_text(law_elem, "법령ID"),
            "법령일련번호": get_text(law_elem, "법령일련번호"),
            "공포일자": get_text(law_elem, "공포일자"),
            "공포번호": get_text(law_elem, "공포번호"),
            "제개정구분명": get_text(law_elem, "제개정구분명"),
            "소관부처명": get_text(law_elem, "소관부처명"),
            "법령구분명": get_text(law_elem, "법령구분명"),
            "시행일자": get_text(law_elem, "시행일자"),
        }
        laws.append(law_data)
    
    return {
        "total_count": len(laws),
        "laws": laws,
    }


def get_law_text(mst: str, api_key: str, jo: str | None = None) -> dict[str, Any]:
    """Get detailed law text using MST (law serial number)."""
    params = {
        "target": "eflaw",
        "OC": api_key,
        "type": "JSON",
        "MST": mst,
    }
    if jo:
        params["JO"] = jo
    
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
    # Remove characters that are invalid in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
    sanitized = sanitized.strip()
    return sanitized


def save_law_to_json(law_data: dict[str, Any], output_dir: Path) -> Path:
    """Save law data to JSON file."""
    law_name = law_data.get("법령명한글", "unknown")
    law_id = law_data.get("법령ID", "unknown")
    
    filename = f"{sanitize_filename(law_name)}_{law_id}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(law_data, f, ensure_ascii=False, indent=2)
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Collect Korean law data from Law.go.kr Open API"
    )
    parser.add_argument(
        "--keyword",
        required=True,
        help="Search keyword for laws (e.g., '민법', '형법')",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of laws to collect (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw/laws",
        help="Output directory for JSON files (default: data/raw/laws)",
    )
    parser.add_argument(
        "--fetch-details",
        action="store_true",
        help="Fetch detailed law text for each result",
    )
    
    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get API key
    api_key = get_api_key()
    
    print(f"Searching for laws with keyword: '{args.keyword}'")
    print(f"Limit: {args.limit}")
    print(f"Output directory: {output_dir}")
    
    # Search for laws
    search_result = search_laws(args.keyword, api_key, display=args.limit)
    
    if not search_result["laws"]:
        print("No laws found.")
        return
    
    print(f"Found {search_result['total_count']} laws")
    
    # Process and save each law
    saved_files = []
    for law_summary in search_result["laws"][:args.limit]:
        law_name = law_summary.get("법령명한글", "Unknown")
        law_mst = law_summary.get("법령일련번호")
        
        print(f"\nProcessing: {law_name} (MST: {law_mst})")
        
        law_data = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "search_keyword": args.keyword,
            },
            "summary": law_summary,
        }
        
        # Fetch detailed text if requested
        if args.fetch_details and law_mst:
            try:
                print(f"  Fetching detailed text...")
                details = get_law_text(law_mst, api_key)
                law_data["detail"] = details
            except Exception as e:
                print(f"  Warning: Could not fetch details: {e}")
        
        # Save to file
        filepath = save_law_to_json(law_data, output_dir)
        saved_files.append(filepath)
        print(f"  Saved: {filepath.name}")
    
    print(f"\n{'='*50}")
    print(f"Completed! Saved {len(saved_files)} law files to {output_dir}")


if __name__ == "__main__":
    main()
