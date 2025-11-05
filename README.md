# Tech_ticket — Веб-приложение для постановки и отслеживания задач техспециалистам

**Tech_ticket** — это простое веб-приложение для создания, распределения, выполнения и ведения истории технических заявок (инцидентов, ремонтов, обслуживания).

---

## Функционал

1. **Аутентификация и роли**
   - Регистрация и вход пользователя
   - Роли: `user`, `manager`, `technician`, `admin`
   - Ограничение доступа к API и страницам по ролям

2. **CRUD для заявок**
   - Создание заявки: доступно всем пользователям
   - Просмотр списка с фильтрацией
   - Просмотр деталей заявки
   - Редактирование: только создатель или менеджер
   - Удаление: только `admin`

3. **Назначение и исполнение**
   - Менеджер назначает исполнителя и изменяет статус
   - Исполнитель принимает задачу, добавляет комментарии, отмечает завершение
   - Менеджер закрывает заявку после проверки

4. **История и лог**
   - Для каждой значимой операции сохраняется запись истории
   - Интерфейс просмотра истории в карточке заявки в хронологическом порядке

5. **Вложения**
   - Загрузка файлов (фото, документы) с ограничением по типу и размеру
   - Хранение в файловой системе

6. **Поиск и фильтрация**
   - Полнотекстовый поиск по заголовку и описанию
   - Фильтры: статус, исполнитель, дата

7. **Панель администратора**
   - Управление пользователями

8. **Логирование и обработка ошибок**
   - Централизованный обработчик ошибок
   - Логи событий сохраняются в файл

## Стек технологий и назначение компонентов

### Язык программирования
- **Python 3.13**

### Backend
- **Фреймворк:** FastAPI — современный, быстрый, типизированный
- **Валидация и схемы:** Pydantic — проверка входных/выходных данных
- **ORM:** SQLAlchemy + Pydantic models — работа с БД и сериализация
- **Миграции:** Alembic — управление схемой базы данных
- **Аутентификация:** JWT — токены доступа, проверка ролей
- **Логирование:** стандартный `logging` — запись событий и ошибок

### База данных
- **SQLite** — для разработки и тестов
- **PostgreSQL** — опционально для продакшена

### Хранение файлов (вложения)
- Локальное хранение в контейнере или на сервере (`/app/uploads`)
- Уникальные имена файлов, путь сохраняется в БД

### API
- **Стиль:** REST JSON
- **Документация:** OpenAPI/Swagger — автогенерация при FastAPI
- **Аутентификация:** `Authorization: Bearer <token>`
- **Версионирование:** `/api/v1/...`

### Frontend
- **Шаблоны:** Jinja2 — серверный HTML
- **UI:** Bootstrap 5 — стили и компоненты
- **JavaScript:** для динамики и взаимодействия
- **Страницы:** список заявок, карточка заявки, форма создания, панель администратора

### Тестирование

- **Фреймворк:** `pytest` — модульные и интеграционные тесты
- **HTTP-тесты:** `httpx` + `pytest-asyncio` — проверка асинхронных API-эндпоинтов
- **Моки:** `pytest-mock` — изоляция зависимостей
- **Покрытие:** `coverage` — анализ покрытия кода

### Пакеты/библиотеки:
- **alembic==1.13.0
- **annotated-doc==0.0.3
- **annotated-types==0.7.0
- **anyio==4.11.0
- **bcrypt==4.1.2
- **certifi==2025.10.5
- **click==8.3.0
- **colorama==0.4.6
- **coverage==7.11.0
- **dnspython==2.8.0
- **ecdsa==0.19.1
- **email-validator==2.3.0
- **fastapi==0.110.0
- **fastapi-cli==0.0.14
- **fastapi-cloud-cli==0.3.1
- **greenlet==3.2.4
- **h11==0.16.0
- **httpcore==1.0.9
- **httptools==0.6.4
- **httpx==0.27.0
- **idna==3.10
- **iniconfig==2.1.0
- **itsdangerous==2.2.0
- **Jinja2==3.1.3
- **Mako==1.3.10
- **markdown-it-py==4.0.0
- **MarkupSafe==3.0.3
- **mdurl==0.1.2
- **orjson==3.11.4
- **packaging==25.0
- **passlib==1.7.4
- **pluggy==1.6.0
- **pyasn1==0.6.1
- **pydantic==2.12.3
- **pydantic-extra-types==2.10.6
- **pydantic-settings==2.11.0
- **pydantic_core==2.41.4
- **pydantic[email]>=2.6.0
- **Pygments==2.19.2
- **pytest==8.0.0
- **pytest-asyncio==0.23.5
- **pytest-mock==3.15.1
- **python-dotenv==1.0.0
- **python-jose==3.3.0
- **python-multipart==0.0.20
- **PyYAML==6.0.3
- **rich==14.2.0
- **rich-toolkit==0.15.1
- **rignore==0.7.1
- **rsa==4.9.1
- **sentry-sdk==2.42.1
- **shellingham==1.5.4
- **six==1.17.0
- **sniffio==1.3.1
- **SQLAlchemy==2.0.44
- **starlette==0.36.3
- **typer==0.20.0
- **typing-inspection==0.4.2
- **typing_extensions==4.15.0
- **ujson==5.11.0
- **urllib3==2.5.0
- **uvicorn==0.27.0
- **watchfiles==1.1.0
- **websockets==15.0.1
- **wheel==0.45.1


## По структуре:

- **app/** — основное приложение.
- **app/main.py**
  - точка входа приложения
  - централизует конфигурацию и маршруты
  - сюда подключаются все роутеры
- **app/api/v1/*.py (auth.py, tickets.py, users.py)**
  - REST API endpoints, возвращают JSON.
  - API для AJAX, мобильных клиентов и тестов
  - использовать Depends(get_db) и Pydantic схемы для валидации.
- **app/core** — содержит конфигурацию, безопасность и логирование, обеспечивая инфраструктурную основу приложения
- **app/db/**
  - app/db/base.py — содержит declarative Base для SQLAlchemy.
  - app/db/session.py — создаёт engine и SessionLocal (SQLite: connect_args={"check_same_thread": False}).
  - отделяет подключение к БД и базовые метаданные; упрощает миграции и тесты.
  - все CRUD-функции получают Session через зависимость get_db (yield, finally close).
- **app/models/** — SQLAlchemy модели (таблицы)
  - user.py: модель User (id, username, email, hashed_password, role, department, created_at).
  - ticket.py: модель Ticket (id, title, description, creator_id, assignee_id, priority, status, created_at, updated_at).
  - comment.py: модель Comment (id, ticket_id, author_id, text, attachment_path, created_at).
  - модель — источник для структуры данных. SQLAlchemy позволяет работать с ORM и явными запросами.
- **app/schemas/** — Pydantic схемы для валидации входящих/исходящих данных
  - auth.py: Token, TokenData, LoginRequest.
  - ticket.py: TicketCreate, TicketUpdate, TicketRead.
  - user.py: UserCreate, UserRead.
  - отделяет формат данных API от внутренних моделей; обеспечивает автодокументацию /docs.
- **app/crud/** — слой доступа к данным (Repository-style)
  - crud_user.py, crud_ticket.py — функции типа create_user(db, ...), get_user_by_id(db, id), list_tickets(db, filters), assign_ticket(db, ticket_id, user_id).
  - инкапсулирует SQL/ORM операции; упрощает тестирование (заменяем на мок) и повторное использование.
  - не делать в маршрутах тяжёлых SQL-операций — использовать CRUD.
- **app/templates/** — Jinja2 шаблоны (HTML)
  - base.html — общий шаблон (header/footer, подключение CSS/JS).
  - index.html, tickets/list.html, tickets/detail.html, auth/login.html — страницы приложения.
  - позволяет быстро сделать понятный UI без SPA.
- **app/static/** — статические файлы
  - css/: стили (Bootstrap или свои).
  - js/: клиентские скрипты (AJAX для подписанных операций).
  - uploads/: загруженные фото (создаётся в runtime).
- **tests/**
  - test_models.py, test_api.py — unit и integration тесты (pytest, httpx for API).
  - автоматические тесты проверяют корректность логики и предотвращают регрессии.
- **.env**
  - хранит локальные переменные окружения (DATABASE_URL=sqlite:///./dev.db, SECRET_KEY=...).
- **requirements.txt**
  - список зависимостей для установки pip install -r requirements.txt.
  

