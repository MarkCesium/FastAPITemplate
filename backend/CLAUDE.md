# Backend — архитектура и правила

## Инструменты

- **Python 3.14**, менеджер зависимостей **uv**
- Настройки **ruff** и **mypy** — в `pyproject.toml`
- **После любых изменений в коде** обязательно прогнать линтер: `ruff format . && ruff check --fix .`

## Архитектура

Слои: **Controller → Service → Repository → DB**

```
src/
├── main.py              # Точка входа: FastAPI app, lifespan, dishka setup
├── api/                 # HTTP-слой (controllers, schemas, exception handlers)
├── core/                # Конфигурация, типы, доменные исключения, общие схемы
├── dependencies/        # Dishka-провайдеры (ConfigProvider, DBProvider, ...)
├── infra/               # Инфраструктура (БД: models, repositories, helper, uow)
└── services/            # Бизнес-логика
```

### api/

HTTP-интерфейс. Каждый домен — отдельная директория с `controllers.py` и `schemas.py`.

- `controllers.py` — роутер с эндпоинтами, использует `DishkaRoute` и `FromDishka[]` для инъекции сервисов
- `schemas.py` — request/response Pydantic-модели, специфичные для API
- `exception_handlers.py` — `register_exception_handlers(app)`, маппинг доменных исключений на HTTP-статусы
- `firewall.py` — зависимости авторизации/аутентификации
- `utils.py` — утилиты (генерация OpenAPI JSON)
- `__init__.py` — агрегация роутеров: `router = APIRouter(prefix="/api")`

Контроллеры **не содержат бизнес-логику** — только валидация входных данных и вызов сервисов.

### core/

Ядро приложения, не зависит от конкретных фреймворков.

- `config.py` — `Settings(BaseSettings)` с вложенными конфигами (`AppConfig`, `PostgresConfig`, `LoggingConfig`). Загружается из `.env` с разделителем `__`
- `exceptions.py` — доменные исключения: `AppError` → `NotFoundError`, `ValidationError`. **Не наследуются от HTTPException** — маппинг на HTTP-статусы только в `exception_handlers.py`
- `types.py` — `IDType = uuid.UUID`, `UNSET` sentinel для patch-операций
- `schemas/` — общие Pydantic-схемы (`PaginatedResponse[T]`)

### dependencies/

Dishka DI-провайдеры. Каждый провайдер — отдельный файл.

- `ConfigProvider` — `Settings` (scope: APP)
- `DBProvider` — `DatabaseHelper` (scope: APP), `UnitOfWork` (scope: REQUEST)
- При добавлении нового провайдера — зарегистрировать в `main.py` (`make_async_container`) и экспортировать через `__init__.py`

Скоупы: **APP** для синглтонов (конфигурация, DB helper, HTTP-клиенты), **REQUEST** для per-request (UoW, сервисы).

### infra/

Инфраструктурный слой — реализации работы с внешними системами.

#### infra/db/

- `helper.py` — `DatabaseHelper`: создаёт async engine и session factory
- `uow.py` — `UnitOfWork(session_factory)`: AsyncContextManager, управляет сессией. В `__aenter__` создаёт сессию и инициализирует репозитории. В `__aexit__` коммитит при успехе, откатывает при исключении
- `models/base.py` — `Base(DeclarativeBase)` с UUID7 PK. Все модели наследуются от `Base`
- `models/__init__.py` — экспорт всех моделей с `__all__`
- `repositories/base.py` — `BaseRepository[T: Base]`: generic CRUD (`get_by_id`, `find`, `get_all`, `get_one_or_none`, `create`, `update`, `patch`, `delete`, `count`). **Без** try/except обёрток — исключения пробрасываются естественно
- `repositories/__init__.py` — экспорт всех репозиториев с `__all__`

При добавлении новой модели:
1. Создать файл в `infra/db/models/`
2. Экспортировать из `models/__init__.py`
3. Создать репозиторий в `infra/db/repositories/` (наследуется от `BaseRepository[Model]`)
4. Экспортировать из `repositories/__init__.py`
5. Добавить репозиторий как атрибут в `UnitOfWork.__aenter__`

### services/

Бизнес-логика. Сервисы получают `UnitOfWork` через DI и работают с репозиториями через `async with self.uow as uow:`.

```python
class ExampleService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_item(self, item_id: IDType) -> Item:
        async with self.uow as uow:
            item = await uow.items.get_by_id(item_id)
            if item is None:
                raise NotFoundError(f"Item {item_id} not found")
            return item
```

При добавлении нового сервиса — создать dishka-провайдер в `dependencies/` (scope: REQUEST).

## Стиль кода

- **Type hints** — полные, Python 3.14+ generics (`class Foo[T]: ...`)
- **Re-raise** — всегда `raise ... from e`
- **f-строки в логгере** — не использовать. Правильно: `logger.error("Failed: %s", err)`
- **`__init__.py`** — все пакеты, которые реэкспортируют, используют `__all__` кортежи
- **patch** — использовать `UNSET` sentinel, не `None` (None может быть валидным значением)
- **Миграции** — именуются по дате: `YYYY_MM_DD_HHMM-rev_slug.py`
- **datetime** — всегда UTC с timezone (`DateTime(timezone=True)`)

## Обязательные правила

- **Атомарные операции в БД:** не делать SELECT + DELETE по тем же условиям — использовать `DELETE ... RETURNING`. Два запроса создают race condition
- **Контроллеры — тонкие:** только валидация и вызов сервиса, бизнес-логика живёт в `services/`
- **Исключения — доменные:** бросать `NotFoundError` / `ValidationError`, а не `HTTPException`. Маппинг на HTTP-статусы — только в `exception_handlers.py`
- **Транзакции — через UoW:** не вызывать `session.commit()` напрямую, всё через `async with self.uow`
