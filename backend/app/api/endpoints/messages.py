from fastapi import APIRouter

router = APIRouter()

@router.get("/{conversation_id}")
async def get_messages(conversation_id: str):
    return []
