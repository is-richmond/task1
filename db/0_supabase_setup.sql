-- ШАГ 3: Выполни этот SQL в Supabase → SQL Editor
-- https://app.supabase.com/project/mudmipuwcfcgsgqxuahj/sql/new

CREATE TABLE IF NOT EXISTS orders (
    id          TEXT PRIMARY KEY,
    number      TEXT,
    status      TEXT,
    created_at  TIMESTAMP,
    first_name  TEXT,
    last_name   TEXT,
    phone       TEXT,
    email       TEXT,
    city        TEXT,
    utm_source  TEXT,
    total       NUMERIC DEFAULT 0,
    currency    TEXT DEFAULT 'KZT',
    items       JSONB,
    synced_at   TIMESTAMP DEFAULT NOW()
);

-- Индексы для быстрой фильтрации
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_total ON orders(total DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Разрешаем чтение для anon (нужно для дашборда)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon read" ON orders
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow service write" ON orders
    FOR ALL TO service_role USING (true);

-- Проверка (должна вернуть пустую таблицу)
SELECT COUNT(*) FROM orders;
