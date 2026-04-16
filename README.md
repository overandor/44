# Local-First AI Monetization Starter (Production-ish)

Этот репозиторий — upgrade от MVP к более взрослой архитектуре для платного local-first AI продукта.

## Что добавлено для уровня "можно продавать"

- License API разделён на слои (`config`, `schemas`, `store`, `service`, `security`).
- Лицензии хранятся в `backend/data/licenses.json` (демо-persistency вместо in-memory).
- Проверка seat limit (привязка устройств через `machine_hash`).
- Подписанный grant (HMAC-SHA256), который клиент валидирует локально.
- Offline fallback по кэшу до `grace_until`.
- Базовые тесты для ключевых edge cases.

## Структура

```text
backend/
  app/
    config.py
    schemas.py
    security.py
    service.py
    store.py
  tests/
    test_license_service.py
  main.py
local_client/
  license.py
```

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8080
```

Проверка:

```bash
curl -X POST http://127.0.0.1:8080/v1/license/check \
  -H "x-api-token: dev-token-change-me" \
  -H "Content-Type: application/json" \
  -d '{"license_key":"DEV-PRO-123","machine_hash":"abcabcabcabcabcabc","app_version":"0.2.0"}'
```

## Тесты

```bash
pytest -q
```

## Как двигаться к "$100k codebase"

- Вынести store в PostgreSQL + миграции (Alembic).
- Добавить billing интеграции (Stripe/LemonSqueezy webhooks).
- Добавить admin API для выдачи/revoke ключей.
- Ввести audit trails и rate limiting.
- Выпуск desktop оболочки (Tauri/Electron) + авто-обновления.
- Телеметрия активаций/retention (privacy-preserving).
