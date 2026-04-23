# Шаблон для fastapi проектов

Структура проекта
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
├── .docker-compose.xml
├── Dockerfile
├── .env
├── .gitignore
├── .dockergitignore
└── alembic.ini
```
