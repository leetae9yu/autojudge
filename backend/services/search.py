"""Search service for laws and precedents."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from config import settings


@dataclass
class SearchResult:
    """Search result item."""

    id: str
    title: str
    content: str
    source: str
    metadata: dict[str, Any]
    score: float


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Tuple of (frontmatter dict, body content)
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if match:
        frontmatter_text = match.group(1)
        body = match.group(2)
        try:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            frontmatter = {}
        return frontmatter, body

    return {}, content


def extract_keywords(text: str) -> list[str]:
    """Extract keywords from text for simple keyword matching.

    Args:
        text: Input text

    Returns:
        List of keywords ( Korean words and alphanumeric sequences)
    """
    # Extract Korean words (2+ characters) and alphanumeric words
    korean_words = re.findall(r"[가-힣]{2,}", text)
    alphanumeric = re.findall(r"[a-zA-Z0-9]{2,}", text)

    # Combine and deduplicate
    keywords = list(set(korean_words + alphanumeric))
    return keywords


def calculate_score(text: str, keywords: list[str]) -> float:
    """Calculate relevance score based on keyword matches.

    Args:
        text: Text to search in
        keywords: Keywords to match

    Returns:
        Score based on keyword frequency
    """
    if not keywords:
        return 0.0

    text_lower = text.lower()
    score = 0.0

    for keyword in keywords:
        # Exact match gets higher score
        count = text_lower.count(keyword.lower())
        score += count * 1.0

        # Partial match gets lower score
        if len(keyword) > 2:
            partial_count = sum(
                1 for word in text_lower.split() if keyword.lower() in word
            )
            score += partial_count * 0.5

    # Normalize by number of keywords
    return score / len(keywords)


def load_markdown_files(directory: Path) -> list[tuple[dict[str, Any], str, Path]]:
    """Load all markdown files from directory.

    Args:
        directory: Directory to search

    Returns:
        List of (frontmatter, content, path) tuples
    """
    results = []

    if not directory.exists():
        return results

    for file_path in directory.glob("*.md"):
        # Skip README files
        if file_path.name.lower() == "readme.md":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(content)
            results.append((frontmatter, body, file_path))
        except Exception:
            continue

    return results


def search_laws(query: str, top_k: int = 5) -> list[SearchResult]:
    """Search for relevant laws based on query.

    Args:
        query: Search query text
        top_k: Maximum number of results

    Returns:
        List of search results
    """
    keywords = extract_keywords(query)
    laws_dir = settings.database_path / "laws"
    laws = load_markdown_files(laws_dir)

    scored_results = []

    for frontmatter, content, file_path in laws:
        # Build searchable text from metadata and content
        law_name = frontmatter.get("name", "")
        law_id = frontmatter.get("id", file_path.stem)
        searchable_text = f"{law_name} {content}"

        # Calculate score
        score = calculate_score(searchable_text, keywords)

        if score > 0:
            result = SearchResult(
                id=law_id,
                title=law_name or file_path.stem,
                content=content[:1000] + "..." if len(content) > 1000 else content,
                source=str(file_path.relative_to(settings.database_path)),
                metadata={
                    "type": frontmatter.get("type", "법률"),
                    "department": frontmatter.get("department", ""),
                    "date_promulgated": frontmatter.get("date_promulgated", ""),
                    "date_enforced": frontmatter.get("date_enforced", ""),
                },
                score=score,
            )
            scored_results.append(result)

    # Sort by score descending and return top_k
    scored_results.sort(key=lambda x: x.score, reverse=True)
    return scored_results[:top_k]


def search_precedents(query: str, top_k: int = 5) -> list[SearchResult]:
    """Search for relevant precedents based on query.

    Args:
        query: Search query text
        top_k: Maximum number of results

    Returns:
        List of search results
    """
    keywords = extract_keywords(query)
    precedents_dir = settings.database_path / "precedents"
    precedents = load_markdown_files(precedents_dir)

    scored_results = []

    for frontmatter, content, file_path in precedents:
        # Build searchable text from metadata and content
        case_name = frontmatter.get("case_name", "")
        case_number = frontmatter.get("case_number", "")
        court = frontmatter.get("court", "")
        holding = frontmatter.get("holding", "")
        summary = frontmatter.get("summary", "")
        precedent_id = frontmatter.get("id", file_path.stem)

        searchable_text = f"{case_name} {case_number} {court} {holding} {summary} {content}"

        # Calculate score
        score = calculate_score(searchable_text, keywords)

        if score > 0:
            result = SearchResult(
                id=precedent_id,
                title=case_name or file_path.stem,
                content=content[:1000] + "..." if len(content) > 1000 else content,
                source=str(file_path.relative_to(settings.database_path)),
                metadata={
                    "case_number": case_number,
                    "court": court,
                    "date_judgment": frontmatter.get("date_judgment", ""),
                    "judgment_type": frontmatter.get("judgment_type", ""),
                    "holding": holding,
                    "summary": summary,
                },
                score=score,
            )
            scored_results.append(result)

    # Sort by score descending and return top_k
    scored_results.sort(key=lambda x: x.score, reverse=True)
    return scored_results[:top_k]


def search(
    query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """Search for relevant laws and precedents.

    Args:
        query: Search query text
        top_k: Maximum number of results per category

    Returns:
        Dictionary with laws, precedents, and query
    """
    laws = search_laws(query, top_k)
    precedents = search_precedents(query, top_k)

    return {
        "query": query,
        "laws": [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content,
                "source": r.source,
                "metadata": r.metadata,
                "score": r.score,
            }
            for r in laws
        ],
        "precedents": [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content,
                "source": r.source,
                "metadata": r.metadata,
                "score": r.score,
            }
            for r in precedents
        ],
    }
