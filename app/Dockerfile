# pull official base image
#3.14.6-slim-trixie
FROM python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144 AS builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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
    && apt-get clean 


    

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# dev dependencies
COPY ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN dos2unix /usr/src/app/entrypoint.sh && \
    chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
