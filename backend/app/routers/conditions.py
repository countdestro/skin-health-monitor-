"""
GET /conditions — list all skin diseases.
GET /conditions/{name}/remedies — get static + optional web-fetched cures for a condition.
"""
from fastapi import APIRouter, Query

from app.schemas import success_response, error_response
from app.services.web_remedy_service import (
    get_all_conditions,
    get_condition_by_name,
    get_static_remedies,
    fetch_cures_from_internet,
)

router = APIRouter(prefix="/conditions", tags=["conditions"])


@router.get("", response_model=None)
def list_conditions():
    """Return all recognised skin conditions with id, name, aliases, and remedy count."""
    conditions = get_all_conditions()
    items = [
        {
            "id": c["id"],
            "name": c["name"],
            "aliases": c.get("aliases", []),
            "remedy_count": len(c.get("remedies", [])),
        }
        for c in conditions
    ]
    return success_response({"conditions": items, "total": len(items)})


@router.get("/{condition_name}/remedies", response_model=None)
async def get_remedies(
    condition_name: str,
    fetch_web: bool = Query(True, description="Fetch treatment summary from Wikipedia"),
):
    """Get remedies for a skin condition. Static from DB + optional Wikipedia summary if fetch_web=true."""
    cond = get_condition_by_name(condition_name)
    if not cond:
        return error_response("NOT_FOUND", f"Condition not found: {condition_name}", {"condition": condition_name})

    static = get_static_remedies(condition_name)
    result = {
        "condition": cond["name"],
        "aliases": cond.get("aliases", []),
        "remedies": static,
        "source": "local",
    }

    if fetch_web:
        web = await fetch_cures_from_internet(cond["name"])
        result["cures_from_internet"] = {
            "source": web["source"],
            "summary": web["summary"],
            "url": web["url"],
            "success": web["success"],
            "error": web.get("error"),
        }

    return success_response(result)
