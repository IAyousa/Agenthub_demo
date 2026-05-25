from fastapi import APIRouter

router = APIRouter()

@router.get("/{artifact_id}")
async def get_artifact(artifact_id: str):
    return {}
