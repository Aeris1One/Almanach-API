FROM python:3.12-slim-bullseye

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /backend/requirements.txt

COPY ./app /backend/app

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=5s --retries=3 CMD curl --fail http://localhost:80/health || exit 1
CMD ["fastapi", "run", "app/main.py"]