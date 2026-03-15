"""
Fetch skin condition treatment/cure information from the internet.
Uses Wikipedia REST API (no API key required) for reliable, readable summaries.
"""
import json
import logging
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
_cached_web_remedies: dict[str, dict] = {}


def _load_conditions_data() -> list[dict]:
    """Load skin conditions and their Wikipedia titles from JSON."""
    path = Path(__file__).resolve().parent.parent / "data" / "skin_conditions.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("conditions", [])


def get_condition_by_name(name: str) -> Optional[dict]:
    """Return condition dict from data by name or alias (case-insensitive)."""
    conditions = _load_conditions_data()
    name_lower = name.strip().lower()
    for c in conditions:
        if c.get("name", "").lower() == name_lower:
            return c
        for alias in c.get("aliases", []):
            if alias.lower() == name_lower:
                return c
    return None


def get_all_conditions() -> list[dict]:
    """Return all skin conditions with id, name, aliases, remedies, wikipedia_title."""
    return _load_conditions_data()


def get_static_remedies(condition_name: str) -> list[str]:
    """Get static remedies for a condition from our JSON (offline)."""
    cond = get_condition_by_name(condition_name)
    if cond:
        return list(cond.get("remedies", []))
    return [
        "Keep skin clean and moisturised.",
        "Use broad-spectrum SPF in sun.",
        "Consult a dermatologist for personalised advice.",
    ]


async def fetch_cures_from_internet(condition_name: str) -> dict:
    """Fetch treatment/cure information from Wikipedia. Returns source, summary, url, success, error."""
    cond = get_condition_by_name(condition_name)
    title = None
    if cond:
        title = cond.get("wikipedia_title") or condition_name.replace(" ", "_")
    else:
        title = condition_name.replace(" ", "_")

    treatment_title = f"{title}_treatment" if "_treatment" not in title else title
    cache_key = treatment_title
    if cache_key in _cached_web_remedies:
        return _cached_web_remedies[cache_key]

    result = {
        "source": "wikipedia",
        "title": treatment_title.replace("_", " "),
        "summary": "",
        "url": f"https://en.wikipedia.org/wiki/{treatment_title.replace(' ', '_')}",
        "success": False,
        "error": None,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(WIKI_SUMMARY_URL.format(title=treatment_title))
            if resp.status_code == 404:
                resp = await client.get(WIKI_SUMMARY_URL.format(title=title))
            resp.raise_for_status()
            data = resp.json()
            result["summary"] = (data.get("extract") or "").strip()
            result["success"] = bool(result["summary"])
            if data.get("content_urls", {}).get("desktop", {}).get("page"):
                result["url"] = data["content_urls"]["desktop"]["page"]
    except httpx.HTTPStatusError as e:
        result["error"] = f"HTTP {e.response.status_code}"
        logger.warning("Wikipedia API error for %s: %s", treatment_title, e)
    except Exception as e:
        result["error"] = str(e)
        logger.warning("Failed to fetch remedies for %s: %s", condition_name, e)

    _cached_web_remedies[cache_key] = result
    return result


def get_remedies_for_condition(condition_name: str) -> dict:
    """Synchronous helper: return static remedies only (no network)."""
    remedies = get_static_remedies(condition_name)
    cond = get_condition_by_name(condition_name)
    return {
        "condition": condition_name,
        "remedies": remedies,
        "source": "local",
        "wikipedia_title": cond.get("wikipedia_title") if cond else None,
    }
