#3.14.6-slim-trixie
FROM python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144

WORKDIR /app

# Dépendances système pour le traitement audio
ARG PDM_VERSION=2.28.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/* && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --only-binary :all: --no-cache-dir "pdm==${PDM_VERSION}"
  

COPY pyproject.toml pdm.lock ./
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"
RUN pdm sync --dev --no-editable

COPY main.py .
COPY app/ ./app/
COPY tests/ ./tests/

# Pré-télécharge le modèle au build pour un démarrage rapide
ARG CLAP_MODEL=laion/clap-htsat-unfused
ENV CLAP_MODEL=${CLAP_MODEL}

RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /tmp/pytest-cache && \
    chown -R appuser:appuser /app /tmp/pytest-cache

ENV PYTEST_ADDOPTS="-o cache_dir=/tmp/pytest-cache"

USER appuser

RUN python -c "\
from transformers import ClapModel, ClapProcessor; \
ClapProcessor.from_pretrained('${CLAP_MODEL}'); \
ClapModel.from_pretrained('${CLAP_MODEL}')"



EXPOSE 8089

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8089"]
