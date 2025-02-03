
# Description 



# Installation

create *.env* file
```shell
cp .env.dev.sample .env

```


launch docker
```shell
    docker compose up --build 
```

go in the container 
```shell
docker exec -it django-web-1 bash
```

create a super user 
```shell
python manage.py createsuperuser
```



# URL
port a modificer selon .env
## App
http://localhost:8000/

## RabbitMQ
http://localhost:15672/

## MailHog 
http://localhost:8025/
