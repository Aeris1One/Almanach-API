from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Almanach API",
    description="Agrégat des bases de données multimodales en open data",
    version="0.1.0-alpha",
    contact={
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL
    }
)

# CORS
origins = [origin.scheme + "://" + origin.host + ":" + str(origin.port) for origin in settings.BACKEND_CORS_ORIGINS]
print(origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Redirection vers la documentation
@app.get("/", include_in_schema=False, status_code=302, response_class=RedirectResponse)
async def root():
    return "/docs"


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/v1")
