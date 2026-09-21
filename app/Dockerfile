# pull official base image
#3.14.6-slim-trixie
FROM python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144 AS builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG PDM_VERSION=2.28.2

# install system dependencies
RUN apt-get update && apt-get --no-install-recommends install -y build-essential --purge cron \
    dos2unix \
    ffmpeg \
    gettext \
    libjpeg62-turbo-dev \
    netcat-openbsd \
    portaudio19-dev \
    procps\
    rsyslog\
    systemd \
    zlib1g-dev \
    # clean cache
    && apt-get clean \
    # PDM
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install --only-binary :all: --no-cache-dir "pdm==${PDM_VERSION}"

COPY pyproject.toml pdm.lock ./
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"
RUN pdm sync --dev --no-editable

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN dos2unix /usr/src/app/entrypoint.sh && \
    chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
