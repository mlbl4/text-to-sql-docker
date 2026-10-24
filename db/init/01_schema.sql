-- =============================================================
-- 01_schema.sql — Online store schema
-- Runs automatically the FIRST time the PostgreSQL container
-- starts with an empty data volume (/docker-entrypoint-initdb.d).
-- =============================================================

-- Customers of the store
CREATE TABLE customers (
    customer_id  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name   VARCHAR(50)  NOT NULL,
    last_name    VARCHAR(50)  NOT NULL,
    email        VARCHAR(100) NOT NULL UNIQUE,
    city         VARCHAR(50)  NOT NULL,
    signup_date  DATE         NOT NULL
);

-- Product categories (each category exists only once)
CREATE TABLE categories (
    category_id  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(50) NOT NULL UNIQUE
);

-- Products, each belonging to one category
CREATE TABLE products (
    product_id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    category_id  INT           NOT NULL REFERENCES categories(category_id),
    unit_price   NUMERIC(10,2) NOT NULL CHECK (unit_price > 0)   -- current price
);

-- Orders placed by customers
CREATE TABLE orders (
    order_id     INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  INT         NOT NULL REFERENCES customers(customer_id),
    order_date   DATE        NOT NULL,
    status       VARCHAR(20) NOT NULL
                 CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled'))
);

-- Lines of each order: which product, how many, at what price
CREATE TABLE order_items (
    order_item_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id      INT           NOT NULL REFERENCES orders(order_id),
    product_id    INT           NOT NULL REFERENCES products(product_id),
    quantity      INT           NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price > 0)  -- price at the moment of the sale
);

-- Indexes on foreign keys (PostgreSQL does not create them automatically)
CREATE INDEX idx_products_category    ON products(category_id);
CREATE INDEX idx_orders_customer      ON orders(customer_id);
CREATE INDEX idx_orders_date          ON orders(order_date);
CREATE INDEX idx_order_items_order    ON order_items(order_id);
CREATE INDEX idx_order_items_product  ON order_items(product_id);
