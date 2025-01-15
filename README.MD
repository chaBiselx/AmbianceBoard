
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


