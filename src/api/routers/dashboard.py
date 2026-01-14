from fastapi import APIRouter, HTTPException

from src.api.utils.history import history_manager

router = APIRouter()


@router.get("/recent")
async def get_recent_history(limit: int = 10, type: str | None = None):
    return history_manager.get_recent(limit, type)


@router.get("/{entry_id}")
async def get_history_entry(entry_id: str):
    entry = history_manager.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.delete("/delete/{entry_id}")
async def delete_history_entry(entry_id: str):
    """Delete a single history entry by ID."""
    success = history_manager.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"success": True, "message": "Entry deleted"}


@router.delete("/delete-by-type")
async def delete_by_type(type: str | None = None):
    """Delete all entries of a specific type, or all if type is 'all'."""
    if type == "all":
        deleted_count = history_manager.delete_by_type(None)
    else:
        deleted_count = history_manager.delete_by_type(type)
    return {"success": True, "deleted_count": deleted_count}
