-- ============================================
-- SQL-скрипт БД "shoe_store" для PostgreSQL
-- 3 нормальная форма, ссылочная целостность
-- ============================================

-- Удаление таблиц (если существуют)
DROP TABLE IF EXISTS order_item CASCADE;
DROP TABLE IF EXISTS "order" CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS pickup_point CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS unit CASCADE;
DROP TABLE IF EXISTS supplier CASCADE;
DROP TABLE IF EXISTS manufacturer CASCADE;
DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS role CASCADE;

-- Роли пользователей
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL UNIQUE
);

-- Пользователи (с привязкой к Django auth)
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP NOT NULL DEFAULT NOW(),
    patronymic VARCHAR(150) NOT NULL DEFAULT '',
    role_id INTEGER REFERENCES role(id) ON DELETE SET NULL
);

-- Категории товаров
CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(200) NOT NULL UNIQUE
);

-- Производители
CREATE TABLE manufacturer (
    id SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(200) NOT NULL UNIQUE
);

-- Поставщики
CREATE TABLE supplier (
    id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL UNIQUE
);

-- Единицы измерения
CREATE TABLE unit (
    id SERIAL PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL UNIQUE
);

-- Товары
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    article VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(300) NOT NULL,
    unit_id INTEGER NOT NULL REFERENCES unit(id) ON DELETE RESTRICT,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    supplier_id INTEGER NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturer(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES category(id) ON DELETE RESTRICT,
    discount NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 100),
    quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantity_in_stock >= 0),
    description TEXT NOT NULL DEFAULT '',
    photo VARCHAR(100) NULL
);

-- Пункты выдачи
CREATE TABLE pickup_point (
    id SERIAL PRIMARY KEY,
    address VARCHAR(500) NOT NULL
);

-- Заказы
CREATE TABLE "order" (
    id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    delivery_date DATE NULL,
    pickup_point_id INTEGER NOT NULL REFERENCES pickup_point(id) ON DELETE RESTRICT,
    client_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT,
    pickup_code INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Новый'
);

-- Позиции заказа
CREATE TABLE order_item (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES "order"(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

-- Индексы
CREATE INDEX idx_product_category ON product(category_id);
CREATE INDEX idx_product_supplier ON product(supplier_id);
CREATE INDEX idx_product_manufacturer ON product(manufacturer_id);
CREATE INDEX idx_order_client ON "order"(client_id);
CREATE INDEX idx_order_item_order ON order_item(order_id);
CREATE INDEX idx_order_item_product ON order_item(product_id);
CREATE INDEX idx_user_role ON "user"(role_id);
