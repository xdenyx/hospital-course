# API ендпойнти
Базовий префікс: `/api/`

Аутентифікація
- Виняток: `POST /api/login/`.

Примітка
-  (`/admin/`) — окремий інтерфейс керування

## 1. Авторизація
- `POST /api/login/` — отримати токен.
- `POST /api/logout/` — вийти з системи.

## 2. Пацієнти
- `GET /api/patients/` — список пацієнтів.
- `POST /api/patients/` — створити пацієнта.
- `GET /api/patients/{id}/` — деталі пацієнта.
- `PUT /api/patients/{id}/` — оновити пацієнта.
- `PATCH /api/patients/{id}/` — частково оновити пацієнта.
- `GET /api/patients/by-work/` — вибірка пацієнтів за роботою і датою.
- `GET /api/patients/{id}/protocol/` — протокол пацієнта.

## 2.1. Лікарі
- `GET /api/doctors/` — список лікарів.
- `GET /api/doctors/{id}/` — деталі лікаря.
- використовується у фронтенді для вибору лікаря під час створення або редагування заявки.

## 3. Заявки
- `GET /api/requests/` — список заявок.
- `GET /api/requests/{id}/` — деталі заявки.

## 3.1. Заявки (admin-only зміни)
- Створення, оновлення і видалення заявок виконується через `/admin/`.

## 4. Прийоми
- `GET /api/appointments/` — список прийомів.
- `GET /api/appointments/{id}/` — деталі прийому.

## 4.1. Прийоми (admin-only зміни)
- Створення, оновлення і видалення прийомів виконується через `/admin/`.

## 5. Роботи в прийомі
- `GET /api/appointment-works/` — список робіт.
- `GET /api/appointment-works/{id}/` — деталі роботи.

## 5.1. Роботи в прийомі (admin-only зміни)
- Створення, оновлення і видалення робіт виконується через `/admin/`.

## 6. Матеріали до робіт
- `GET /api/work-materials/` — список матеріалів.
- `GET /api/work-materials/{id}/` — деталі матеріалу.

## 6.1. Матеріали до робіт (admin-only зміни)
- Створення, оновлення і видалення матеріалів виконується через `/admin/`.

## 7. Ліки до робіт
- `GET /api/work-medicines/` — список ліків.
- `GET /api/work-medicines/{id}/` — деталі ліків.

## 7.1. Ліки до робіт (admin-only зміни)
- Створення, оновлення і видалення ліків виконується через `/admin/`.

## 8. Процедури до робіт
- `GET /api/work-procedures/` — список процедур.
- `GET /api/work-procedures/{id}/` — деталі процедури.

## 8.1. Процедури до робіт (admin-only зміни)
- Створення, оновлення і видалення процедур виконується через `/admin/`.

## 9. Довідники
- `GET /api/work-categories/` — категорії робіт.
- `GET /api/material-categories/` — категорії матеріалів.
- `GET /api/medicine-categories/` — категорії ліків.
- `GET /api/procedure-categories/` — категорії процедур.

## 10. Звіти
- `GET /api/reports/work-financials/` — фінансовий звіт по категоріях робіт.

## 11. Документація API
- `GET /api/schema/` — OpenAPI schema.
- `GET /api/docs/` — Swagger UI.
- `GET /api/redoc/` — ReDoc.

