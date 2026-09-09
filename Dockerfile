FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN groupadd --system --gid 10001 aegis \
    && useradd --system --uid 10001 --gid aegis --home-dir /nonexistent aegis

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY packages ./packages
RUN python -m pip install --upgrade pip \
    && python -m pip install . uvicorn

USER 10001:10001
EXPOSE 8080
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]
