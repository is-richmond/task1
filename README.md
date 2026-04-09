# RetailCRM Orders Integration System

Комплексная система для загрузки заказов в RetailCRM, синхронизации с Supabase, управления через Telegram бота и веб-дашборда на React.

**Ключевая особенность:** 📊 Дашборд работает **независимо от бэкенда** - показывает заказы из Supabase даже при отключенном сервере!

## 📁 Структура проекта

```
task1/
├── backend/                        # Python backend (Flask API)
│   ├── .env                        # Переменные окружения (локально)
│   ├── .env.example                # Шаблон переменных окружения
│   ├── config.py                   # Конфигурация из .env
│   ├── requirements.txt             # Python зависимости
│   ├── app.py                      # Flask API приложение
│   └── scripts/
│       ├── __init__.py
│       ├── upload_orders.py        # Скрипт загрузки заказов
│       ├── sync_to_supabase.py     # Синхронизация с Supabase
│       └── telegram_bot.py         # Telegram бот
│
├── frontend/                       # React приложение
│   ├── .env                        # Переменные окружения
│   ├── .env.example                # Шаблон переменных окружения
│   ├── package.json                # npm зависимости
│   ├── vite.config.js              # Vite конфигурация
│   ├── index.html                  # HTML точка входа
│   └── src/
│       ├── main.jsx                # React точка входа
│       ├── App.jsx                 # Главный компонент
│       ├── index.css               # Глобальные стили (с градиентами и анимациями)
│       ├── components/
│       │   ├── UploadOrders.jsx    # Загрузка (проверяет статус бэка)
│       │   ├── OrdersList.jsx      # Список заказов (Supabase)
│       │   └── OrderStats.jsx      # Статистика (Supabase)
│       └── services/
│           ├── api.js              # API клиент (для загрузок)
│           └── supabaseClient.js   # Прямое Supabase подключение (новое!)
│
├── db/
│   └── 0_supabase_setup.sql        # SQL схема Supabase
│
├── data/
│   └── mock_orders.json            # Тестовые данные (50 заказов)
│
├── .gitignore                      # Git исключения
├── README.md                       # Этот файл
└── DASHBOARD_UPDATE.md             # Документация по обновлению дашборда
```

---

## 🔧 Установка и запуск

### 1. Backend setup

```bash
# Перейти в backend директорию
cd backend

# Создать .env файл из примера
cp .env.example .env

# Открыть .env и заполнить значения для:
# RETAILCRM_URL, RETAILCRM_API_KEY, RETAILCRM_SITE_CODE
# SUPABASE_URL, SUPABASE_KEY
# TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (опционально)

# Установить Python зависимости
pip install -r requirements.txt

# Запустить API сервер (порт 5003)
python3 app.py
```

### 2. Frontend setup

```bash
# Перейти в frontend директорию
cd frontend

# Установить npm зависимости
npm install --legacy-peer-deps

# Запустить dev сервер (порт 5173 или 3002)
npm run dev
```

### 3. Только просмотр заказов (без бэкенда)

```bash
# Это работает! Дашборд загружает заказы напрямую из Supabase
cd frontend && npm run dev
```

---

## 📋 Переменные окружения

### Backend (.env)

```env
# RetailCRM
RETAILCRM_URL=https://your-site.retailcrm.ru
RETAILCRM_API_KEY=your-api-key
RETAILCRM_SITE_CODE=your-site-code

# Supabase
SUPABASE_URL=https://your-db.supabase.co
SUPABASE_KEY=your-anon-key

# Telegram (опционально)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

### Frontend (.env)

```env
# API Backend (может быть недоступен, это OK!)
VITE_API_URL=http://localhost:5003

# Supabase (для прямого доступа к заказам)
VITE_SUPABASE_URL=https://your-db.supabase.co
VITE_SUPABASE_KEY=your-anon-key
```

---

## 🚀 API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/api/health` | Проверка статуса API |
| GET | `/api/config` | Получить конфигурацию |
| POST | `/api/orders/upload` | Загрузить заказы (требует бэк!) |
| GET | `/api/orders/supabase` | Получить заказы из Supabase |

---

## 🐛 Решённые проблемы при разработке

### История проблем и их решение

#### **Проблема 1: RetailCRM API - "Не удалось получить код сайта"**

**Ваш промпт:**
```
Помог с API, но вижу ошибку...
```

**Описание ошибки:**
```
❌ Не удалось получить код сайта. Проверь API-ключ.
```

**Причина:**
API endpoint `/api/v5/sites` не существует в этом экземпляре RetailCRM. Код пытался автоматически определить `site_code`.

**Решение:**
- Добавили переменную `RETAILCRM_SITE_CODE` в `.env` файл
- Теперь используем значение из конфига напрямую

```python
# backend/config.py
RETAILCRM_SITE_CODE = os.getenv("RETAILCRM_SITE_CODE", "default")
```

---

#### **Проблема 2: RetailCRM API - OrderType не существует**

**Описание ошибки:**
```json
{
  "success": false,
  "errorMsg": "Order is not loaded",
  "errors": {
    "orderType": "\"OrderType\" with \"code\"=\"eshop-individual\" does not exist."
  }
}
```

**Причина:**
`mock_orders.json` содержал `"orderType": "eshop-individual"`, который не существует в RetailCRM. В системе есть только `main`.

**Решение:**
Перестали отправлять `orderType` в API запросе - позволили RetailCRM выбрать тип по умолчанию.

```python
# backend/scripts/upload_orders.py - УДАЛИЛИ строку:
# "orderType": order.get("orderType", "main"),
```

---

#### **Проблема 3: Timeout - скрипты зависают**

**Описание проблемы:**
API запросы к RetailCRM висели бесконечно, скрипт не отвечал.

**Причина:**
Не было timeout на requests, API иногда отвечает очень долго.

**Решение:**
Добавили `timeout=5` ко всем HTTP запросам обо всех скриптах:

```python
# sync_to_supabase.py
r = requests.get(url, params={"apiKey": RETAILCRM_API_KEY}, timeout=5)

# upload_orders.py
r = requests.post(url, params=params, data=data, timeout=5)
```

---

#### **Проблема 4: Pagination - только 20 заказов вместо 50**

**Ваш промпт:**
```
"почему только 20 ордеров пришло? они же все загрузились в 
retailcrm. я скидываю 50 ордеров, а synced only 20"
```

**Описание проблемы:**
Скрипт синхронизации загружал только первые 20 заказов из RetailCRM.

**Причина:**
Функция `get_orders_from_retailcrm()` не реализовала пагинацию. RetailCRM API возвращает 20 результатов за раз, нужно получить все страницы.

**Решение:**
Реализовали while-loop с пагинацией:

```python
# backend/scripts/sync_to_supabase.py
def get_orders_from_retailcrm():
    orders = []
    page = 1
    while True:
        r = requests.get(
            f"{RETAILCRM_URL}/api/v5/orders",
            params={
                "apiKey": RETAILCRM_API_KEY,
                "page": page,
                "limit": 100
            },
            timeout=5
        )
        data = r.json()
        if not data.get("success"):
            break
        orders.extend(data.get("orders", []))
        if len(data.get("orders", [])) < 100:
            break
        page += 1
    return orders
```

**Результат:** Все 50 заказов теперь синхронизируются ✅

---

#### **Проблема 5: CSS файл повредился после редактирования**

**Описание проблемы:**
CSS файл содержал битые данные после использования `cat >>` с heredoc.

**Причина:**
Ошибка при добавлении CSS через терминальный вывод.

**Решение:**
1. Удалили повреждённый файл
2. Пересоздали CSS с полным стилем (768 строк)
3. Добавили красивые градиенты, анимации, отзывчивый дизайн

```css
/* Новые стили - градиенты и анимации */
:root {
  --primary: #6366f1;
  --secondary: #8b5cf6;
  --success: #10b981;
}

.card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: slideDown 0.3s ease-out;
}
```

---

#### **Проблема 6: Дашборд требует бэкенда для просмотра заказов**

**Ваш промпт:**
```
"так же надо что бы дэшборд работал без бэка, то есть данные с 
supabase отображались и без рабочего бека, но например для 
загрузки ордеров он бы писал что надо запустить бэк"
```

**Описание проблемы:**
Если бэкенд был выключен, дашборд не показывал заказы (все компоненты зависели от API).

**Решение:**
Создали архитектуру с двумя источниками данных:

1. **API Backend** - только для загрузки заказов в RetailCRM
2. **Supabase Client** - для отображения данных напрямую

**Что было сделано:**

✅ **Создана новая служба** (`frontend/src/services/supabaseClient.js`):
```javascript
// Прямое подключение к Supabase, не через API
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
);

export const getOrdersDirectly = async () => {
  const { data } = await supabase
    .from('orders')
    .select('*')
    .order('created_at', { ascending: false });
  return { success: true, orders: data || [], count: data?.length || 0 };
};
```

✅ **Обновлены компоненты** для использования Supabase напрямую:
- `OrdersList.jsx` - показывает заказы из Supabase
- `OrderStats.jsx` - показывает статистику из Supabase
- `UploadOrders.jsx` - проверяет статус бэкенда + показывает сообщение

✅ **Добавлена проверка статуса бэкенда:**
```javascript
const checkBackendStatus = async () => {
  try {
    await getHealth(); // Try to ping backend
    setBackendStatus('connected');
  } catch {
    setBackendStatus('disconnected');
  }
};

// Проверяем каждые 10 секунд
useEffect(() => {
  const interval = setInterval(checkBackendStatus, 10000);
  return () => clearInterval(interval);
}, []);
```

✅ **Информативное UI для пользователя:**
```
⚠️ Backend Not Connected
To upload orders, you need to start the backend server. Run:
cd backend && python3 app.py
```

✅ **Установлена Supabase библиотека:**
```bash
npm install @supabase/supabase-js --legacy-peer-deps
```

✅ **Frontend .env расширен:**
```env
VITE_SUPABASE_URL=https://mudmipuwcfcgsgqxuahj.supabase.co
VITE_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Результат:**
- 📊 Дашборд показывает заказы **БЕЗ бэкенда** ✅
- 📁 Загрузка заказов требует бэк (показывает сообщение) ✅
- 🔄 Синхронизация работает в фоне ✅

---

## ✨ Текущий статус системы

| Компонент | Статус | Описание |
|-----------|--------|---------|
| **RetailCRM API** | ✅ Готово | Загрузка 50 заказов, все 3 попытки работают |
| **Supabase Sync** | ✅ Готово | Все 50 заказов синхронизируются (с пагинацией) |
| **React Frontend** | ✅ Готово | Красивый дизайн с анимациями |
| **Offline Mode** | ✅ Готово | Дашборд работает без бэкенда! |
| **Backend Status** | ✅ Готово | Проверка каждые 10 сек + UI уведомления |
| **Telegram Bot** | ✅ Готово | Уведомления о статусе заказов |
| **Mobile Responsive** | ✅ Готово | Работает на всех устройствах |

---

## 🎯 Как использовать

---

## ✅ Быстрый старт

### Вариант 1: Просмотр заказов (без бэкенда)

```bash
cd frontend
npm run dev
# Откройте http://localhost:3002
# Заказы загружаются напрямую из Supabase ✅
```

### Вариант 2: Полная система (просмотр + загрузка)

```bash
# Terminal 1 - Backend
cd backend
cp .env.example .env
# Заполните .env с вашими ключами RetailCRM и Supabase
pip install -r requirements.txt
python3 app.py

# Terminal 2 - Frontend
cd frontend
npm install --legacy-peer-deps
npm run dev

# Откройте http://localhost:3002
```

### Вариант 3: Загрузить новые заказы в RetailCRM

```bash
cd backend
python3 scripts/upload_orders.py
# ✅ [1/50] ORD-001 | John Doe | 50000 ₸
# ✅ [2/50] ORD-002 | Jane Smith | 75000 ₸
# ... и т.д. ...
```

---

## 📊 Примеры использования

### Просмотр заказов в дашборде

1. Запустите фронтенд (`npm run dev`)
2. Отображается таблица со всеми заказами
3. Сортировка по дате, сумме, имени
4. Фильтр по статусам заказа

### Статистика заказов

- 📦 Всего заказов
- 💰 Общая выручка
- 📈 Средняя стоимость заказа
- 📋 Заказы по статусам

### Загрузка новых заказов

1. Подготовьте JSON файл с заказами
2. Запустите бэкенд (`python3 app.py`)
3. Нажмите "Upload Orders" (при запущенном бэке)
4. Выберите файл и загрузите
5. Заказы появятся в RetailCRM и Supabase через 5-10 сек

---

## 🔒 Безопасность

- ✅ Все ключи в `.env` файлах (не в коде)
- ✅ Supabase KEY в фронтенде - публичный anon key (безопасно)
- ✅ Защита на уровне RLS (Row Level Security) в Supabase
- ✅ Временные таймауты на все API запросы

---

## 📱 Отзывчивость

- ✅ Полная поддержка мобильных (480px+)
- ✅ Адаптивный дизайн для планшетов (768px+)
- ✅ Desktop оптимизация (1200px+)

---

## 🚨 Возможные проблемы и решения

### "Суперба 401 Unauthorized"

**Решение:**
- Проверьте `VITE_SUPABASE_KEY` в `.env`
- Убедитесь, что это **публичный anon key**, не service_role key
- Проверьте `VITE_SUPABASE_URL` - учтите регион и доменное имя

### "Backend Not Connected" сообщение

**Это нормально!** Дашборд работает без бэкенда.

**Если нужна загрузка заказов:**
```bash
cd backend && python3 app.py
```

Через 10 секунд сообщение исчезнет и кнопка загрузки включится.

### "Заказы не обновляются"

**Решение:**
1. Проверьте интернет соединение
2. Нажмите "🔄 Refresh" кнопку или обновите страницу (F5)
3. Проверьте консоль браузера (F12) на ошибки
4. Убедитесь, что backend запущен и синхронизирует заказы

---

## 📚 Дополнительные ресурсы

- 📄 [DASHBOARD_UPDATE.md](DASHBOARD_UPDATE.md) - подробное описание обновлений дашборда
- 🗄️ [0_supabase_setup.sql](db/0_supabase_setup.sql) - SQL схема для Supabase
- 📦 [mock_orders.json](mock_orders.json) - примеры данных (50 заказов)

---

## 🔗 Полезные ссылки

- [RetailCRM API Docs](https://api.retailcrm.ru/docs)
- [Supabase Docs](https://supabase.com/docs)
- [React Docs](https://react.dev)
- [Flask Docs](https://flask.palletsprojects.com)

---

## 👨‍💻 История разработки

### День 1: Базовая структура
- ✅ Загрузка заказов в RetailCRM
- ✅ Структурирование backend/frontend

### День 2: Интеграция
- ✅ Добавлена Supabase синхронизация
- ✅ Создана React админ-панель
- ✅ Добавлен Telegram бот

### День 3: Оптимизация
- ✅ Исправлена пагинация (20→50 заказов)
- ✅ Добавлены таймауты к запросам
- ✅ Улучшена обработка ошибок API

### День 4: Красота и Offline
- ✅ Переработан CSS (768 строк стиля)
- ✅ Добавлены анимации и градиенты
- ✅ **Главное:** Дашборд работает БЕЗ бэкенда!
- ✅ Проверка статуса бэкенда с UI

---

**Готово к production!** 🚀
