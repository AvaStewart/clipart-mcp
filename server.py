"""Clipart MCP server: lets an AI search, view, and tag a folder of clip art.

Set CLIPART_DIR to the folder containing your PNGs and manifest.json
(created by build_manifest.py).
"""
import json
import os
import random
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Image

CLIPART_DIR = Path(os.environ.get("CLIPART_DIR", "./images")).resolve()
MANIFEST = CLIPART_DIR / "manifest.json"

mcp = FastMCP("clipart")


def _load() -> list[dict]:
    if not MANIFEST.exists():
        raise RuntimeError(
            f"No manifest at {MANIFEST}. Run build_manifest.py first "
            "and check the CLIPART_DIR environment variable."
        )
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _save(items: list[dict]) -> None:
    MANIFEST.write_text(json.dumps(items, indent=1), encoding="utf-8")


def _summary(item: dict) -> dict:
    return {
        "path": item["path"],
        "category": item["category"],
        "size": f'{item["width"]}x{item["height"]}',
        "tags": item["tags"],
    }


@mcp.tool()
def list_categories() -> dict:
    """List every clip art category (folder) with how many images it has."""
    counts: dict[str, int] = {}
    for item in _load():
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    return dict(sorted(counts.items()))


@mcp.tool()
def search_clipart(query: str, category: str | None = None, limit: int = 10) -> list[dict]:
    """Search clip art by keyword across tags, category and filename.

    Args:
        query: Space-separated keywords, e.g. "squirrel tree".
        category: Optionally restrict to one category from list_categories.
        limit: Max results to return.
    """
    terms = query.lower().split()
    scored = []
    for item in _load():
        if category and item["category"].lower() != category.lower():
            continue
        haystack = item["tags"] + [item["category"].lower(), item["path"].lower()]
        score = sum(any(t in h for h in haystack) for t in terms)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda s: -s[0])
    return [_summary(i) for _, i in scored[:limit]]


@mcp.tool()
def random_clipart(category: str | None = None, count: int = 5) -> list[dict]:
    """Get random clip art, optionally from one category. Good for chaos."""
    items = _load()
    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]
    return [_summary(i) for i in random.sample(items, min(count, len(items)))]


@mcp.tool()
def view_clipart(path: str) -> Image:
    """Return the actual image so you can look at it. Use a path from search results."""
    full = (CLIPART_DIR / path).resolve()
    if CLIPART_DIR not in full.parents or not full.is_file():
        raise ValueError(f"Not a valid clip art path: {path}")
    return Image(path=str(full))


@mcp.tool()
def tag_clipart(path: str, tags: list[str]) -> str:
    """Add descriptive tags to an image (after viewing it) so future searches find it."""
    items = _load()
    for item in items:
        if item["path"] == path:
            item["tags"] = sorted(set(item["tags"]) | {t.lower().strip() for t in tags})
            _save(items)
            return f"Tagged {path}: {item['tags']}"
    raise ValueError(f"No such image in manifest: {path}")


if __name__ == "__main__":
    mcp.run()
