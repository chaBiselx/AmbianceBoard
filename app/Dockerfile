# pull official base image
FROM python:3.11.4-slim-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get --no-install-recommends install -y build-essential --purge cron \
    dos2unix \
    ffmpeg \
    netcat \
    procps\
    rsyslog\
    systemd \
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
