# Nova Shapewear — Система аналитики заказов

## Структура проекта

```
project/
├── 0_supabase_setup.sql    # SQL для создания таблицы в Supabase
├── 1_upload_orders.py      # Загрузка mock_orders.json → RetailCRM
├── 2_sync_to_supabase.py   # Синхронизация RetailCRM → Supabase
├── 3_dashboard/
│   └── index.html          # Дашборд (деплоится на Vercel)
├── 4_telegram_bot.py       # Бот для уведомлений > 50,000 ₸
└── mock_orders.json        # 50 тестовых заказов
```

---

## Пошаговый запуск

### Шаг 1 — Создай таблицу в Supabase
1. Открой: https://app.supabase.com/project/mudmipuwcfcgsgqxuahj/sql/new
2. Вставь содержимое файла `0_supabase_setup.sql`
3. Нажми **Run**

### Шаг 2 — Загрузи заказы в RetailCRM
```bash
pip install requests
python 1_upload_orders.py
```
Ждёшь ~25 секунд, видишь 50 зелёных ✅

### Шаг 3 — Синхронизируй в Supabase
```bash
pip install requests supabase
python 2_sync_to_supabase.py
```

### Шаг 4 — Задеплой дашборд на Vercel
**Вариант А (через сайт):**
1. Зайди на vercel.com/new
2. Перетащи папку `3_dashboard/`
3. Нажми Deploy

**Вариант Б (через CLI):**
```bash
npm i -g vercel
cd 3_dashboard
vercel --prod
```

### Шаг 5 — Запусти Telegram-бот
```bash
pip install requests
python 4_telegram_bot.py
```
Бот пришлёт стартовое сообщение и будет проверять каждые 60 секунд.

---

## Credentials (уже вшиты в файлы)

| Сервис | Значение |
|--------|----------|
| RetailCRM URL | https://narimandilovarov11.retailcrm.ru |
| Supabase проект | mudmipuwcfcgsgqxuahj |
| Telegram Chat ID | 894877615 |

---

## Тест Telegram-бота вручную

Чтобы проверить что бот работает — создай заказ на сумму > 50,000 ₸ в RetailCRM
и жди до 60 секунд. Придёт уведомление.

Или временно снизь порог в `4_telegram_bot.py`:
```python
THRESHOLD = 10_000  # вместо 50_000
```
