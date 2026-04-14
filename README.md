# Report Generator

REST API сервіс для паралельної генерації звітів з різних джерел даних у різних форматах виводу.

---

## Зміст

- [Архітектура](#архітектура)
- [Структура проєкту](#структура-проекту)
- [Запуск через Docker](#запуск-через-docker)
- [API](#api)
- [Додавання нових джерел, фільтрів та виводів](#розширення)
- [Логування](#логування)

---

## Архітектура

```
HTTP Request (BatchRequest)
        │
        ▼
  POST /reports/batch
        │
        ▼
  run_batch()  ──── asyncio.gather() ────► [run_report(), run_report(), ...]
                                                    │
                                          ┌─────────▼──────────┐
                                          │ Source (fetch)     │  ← CSV / JSON / DB / API
                                          │ Validate (Pydantic)│
                                          │ Filter (apply)     │  ← тип звіту
                                          │ Output (write)     │  ← JSON / CSV / stream
                                          └────────────────────┘
```

Кожен звіт у батчі виконується незалежно та паралельно через `asyncio.gather()`.  
Блокуючий I/O (читання файлів) виноситься у `asyncio.to_thread()`, щоб не блокувати event loop.

Додавання нового джерела/фільтру/виводу зводиться до:
1. Написати клас-спадкоємець від `AbstractSource` / `AbstractFilter` / `AbstractOutput`
2. Зареєструвати його в `app/services/registry.py`

---

## Структура проекту

```
report_generator/
├── app/
│   ├── main.py                  # FastAPI app
│   ├── api/
│   │   └── v1/
│   │       └── endpoints    
│   │           └── reports.py   # POST /reports/batch
│   ├── core/
│   │   ├── config.py            # FastAPI settings
│   │   └── logging.py           # structlog — structured logging з report_id
│   ├── schemas/
│   │   ├── report.py            # BatchRequest, BatchResponse, ReportResult, ...
│   │   └── employee.py          # EmployeeRecord — валідація вхідних рядків
│   ├── sources/
│   │   ├── base.py              # AbstractSource
│   │   └── csv_source.py        # CSVSource ✓ (реалізовано)
│   ├── filters/
│   │   ├── base.py              # AbstractFilter
│   │   └── employees.py         # HighSalaryEmployeeFilter ✓ (salary > 3500)
│   ├── outputs/
│   │   ├── base.py              # AbstractOutput
│   │   └── json_output.py       # JsonOutput ✓ (реалізовано)
│   └── services/
│       ├── registry.py          # Маппінг: тип → клас
│       └── report_service.py    # run_report(), run_batch()
├── input_data.csv               # Приклад вхідних даних
├── output_example.json          # Приклад виводу
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Запуск через Docker

### docker compose (рекомендовано)

```bash
# Клонувати репозиторій
git clone https://github.com/ArtemMint/ReportGenerator.git
cd ReportGenerator

# Збудувати образ і запустити контейнер
docker compose up --build

# У фоні
docker compose up --build -d

# або з переглядом логів
docker compose up --build && docker compose logs -f backend
```

Сервіс буде доступний на `http://localhost:8000`.  

### Зупинити

```bash
docker compose down
```

### Інтерактивна документація

Після запуску відкрийте у браузері:

| URL | Опис |
|-----|------|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |

---

## API

### `POST /reports/batch`

Запускає один або кілька звітів паралельно.

**Тіло запиту:**

```json
{
  "reports": [
    {
      "source": {
        "type": "csv",
        "path": "/code/input_data.csv"
      },
    "filter": {
        "type": "high_salary_employees",
        "salary_threshold": 3500
      },
      "output": {
        "type": "json",
        "path": "/code/"
      }
    }
  ]
}
```

**Статуси звіту:**

| Статус | Опис |
|--------|------|
| `done` | Успішно завершено |
| `failed` | Помилка (деталі у полі `error`) |

---

## Розширення

### Додати нове джерело (наприклад `JsonSource`)

```python
# app/sources/json_source.py
from app.sources.abstract import AbstractSource

class JsonSource(AbstractSource):
    async def fetch(self) -> list[dict]:
        ...
```

```python
# app/services/registry.py
from app.sources import JSONSource, CSVSource

SOURCE_REGISTRY = {
    SourceType.csv:  CSVSource,
    SourceType.json: JSONSource,  # ← додати один рядок
}
```

Аналогічно для `AbstractFilter` та `AbstractOutput`.

---

## Логування

Сервіс використовує [structlog](https://www.structlog.org/) зі structured-форматом.  
Кожен лог-запис містить `report_id`, що дозволяє відстежити lifecycle конкретного звіту:

```
reports_backend  | 2026-04-14T07:13:11.559029Z [info     ] batch.start                    [app.services.report_servise] batch_id=a7d4f0bd-5fb6-4389-a79a-3ad707f313be report_count=1
reports_backend  | 2026-04-14T07:13:11.559261Z [info     ] report.start                   [app.services.report_servise] report_id=182bafeb-7631-426c-9837-f794698070ef
reports_backend  | 2026-04-14T07:13:11.561817Z [warning  ] validation.row_invalid         [app.services.report_servise] error='Value error, Field must be non-negative' field=Salary row=0
reports_backend  | 2026-04-14T07:13:11.565801Z [warning  ] validation.summary             [app.services.report_servise] dropped=[0] invalid_rows=1
reports_backend  | 2026-04-14T07:13:11.566377Z [info     ] report.fetched                 [app.services.report_servise] record_count=99 report_id=182bafeb-7631-426c-9837-f794698070ef
reports_backend  | 2026-04-14T07:13:11.567504Z [info     ] report.filtered                [app.services.report_servise] filtered_count=51 report_id=182bafeb-7631-426c-9837-f794698070ef
reports_backend  | 2026-04-14T07:13:11.569633Z [info     ] report.done                    [app.services.report_servise] report_id=182bafeb-7631-426c-9837-f794698070ef
reports_backend  | 2026-04-14T07:13:11.569789Z [info     ] batch.done                     [app.services.report_servise] batch_id=a7d4f0bd-5fb6-4389-a79a-3ad707f313be done=1 failed=0
```
