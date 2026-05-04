# Шаблон для fastapi проектов

### Структура проекта
```
fastapi-project
├── alembic/
├── src
│   ├── auth
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── repositorires.py
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── users
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── repositorires.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py  # глобальный конфиг
│   ├── exceptions.py  # глобальные ошибки
│   ├── database.py  # подключение к бд и тп
│   └── main.py
├── tests/
│   ├── auth
│   └── users
├── templates/
│   └── index.html
├── requirements.txt
├── .docker-compose.yml
├── Dockerfile
├── .env
├── .gitignore
├── .dockergitignore
└── alembic.ini
```


### Единый формат ошибок:
```
{
  "error": {
    "code": "AUTH_001",
    "status_code": 404,
    "message": "Invalid credentials",
    "details": null,
    "trace_id": uuid
  }
}
```





### .env файл:
```
POSTGRES_HOST=postgres
POSTGRES_USER=postgres
POSTGRES_PASS=postgres
POSTGRES_NAME=defendflow_db
POSTGRES_PORT=5432
POSTGRES_PORTS=5432:5432
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASS}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_NAME}

PEPPER=lol

SECRET_KEY=secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

MAIL_SENDER=user@example.com
EMAIL_PASSWORD=password

REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=10
CACHE_TTL=600
EMAIL_CODE_CACHE_TTL=600
MAX_VERIFICATION_ATTEMPTS=3

RATE_LIMIT_COUNT=50
WINDOW=1
BAN_DURATION=600
```