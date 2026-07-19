FROM python:3.14.6-slim-trixie

WORKDIR /app


# Dépendances système pour le traitement audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip
  

COPY requirements.txt .
RUN pip install --no-cache-dir \
    -r requirements.txt

COPY main.py .
COPY app/ ./app/

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
