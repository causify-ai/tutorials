# ────────────────────────────────────────────────────────────────────────────
# Real‑Time Bitcoin Dashboard  •  DATA605 Spring 2025
# Submission‑grade Dockerfile – minimal, self‑contained, reproducible
# ────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

LABEL maintainer="vikranthreddimasu"
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC

# ---------------------------------------------------------------------------
# 1.  OS packages (keep minimal)
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl tzdata git && \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# 2.  Copy Python dependency list & install (better layer caching)
# ---------------------------------------------------------------------------
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# ---------------------------------------------------------------------------
# 3.  Copy project source code into the image
#     (dot copies everything in build context → keep .dockerignore tidy)
# ---------------------------------------------------------------------------
WORKDIR /app
COPY . .

# ---------------------------------------------------------------------------
# 4.  Expose Dash port & run the dashboard by default
# ---------------------------------------------------------------------------
EXPOSE 8888
CMD ["python3", "bitcoin_dashboard.py"]
