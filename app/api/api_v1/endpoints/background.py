from fastapi import APIRouter

router = APIRouter()


@router.get("/back")
async def root():
    """
    A demo endpoint that starts a background task on the "almanach" queue.
    """
    from app.worker import test_celery

    test_celery.delay("world")
    return {"message": "Background task started"}
