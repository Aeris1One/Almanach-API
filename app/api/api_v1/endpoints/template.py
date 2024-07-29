from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """
    This is a template endpoint that returns a simple message.
    """
    return {"message": "Hello, World!"}
