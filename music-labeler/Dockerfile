FROM python:3.11.4-slim-bullseye

WORKDIR /app


# Dépendances système pour le traitement audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip


# Installe torch CPU séparément (gros download, mieux cacheable)
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.5.0+cpu

COPY requirements.txt .
RUN pip install  \
    -r requirements.txt

COPY main.py .

# Pré-télécharge le modèle au build pour un démarrage rapide
ARG CLAP_MODEL=laion/clap-htsat-unfused
ENV CLAP_MODEL=${CLAP_MODEL}

RUN adduser --disabled-password --gecos '' appuser
USER appuser

RUN python -c "\
from transformers import ClapModel, ClapProcessor; \
ClapProcessor.from_pretrained('${CLAP_MODEL}'); \
ClapModel.from_pretrained('${CLAP_MODEL}')"



EXPOSE 8089

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8089"]
