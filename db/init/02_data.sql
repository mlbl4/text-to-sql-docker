-- =============================================================
-- 02_data.sql — Mock data for the online store
-- Customers, categories and products are written by hand.
-- Orders and order items are generated with a fixed random seed,
-- so every run produces exactly the same data.
-- Order dates are relative to CURRENT_DATE (last 12 months), so
-- questions like "last month" always have data.
-- =============================================================

INSERT INTO categories (name) VALUES
    ('Electronics'),
    ('Books'),
    ('Home'),
    ('Sports'),
    ('Clothing');

INSERT INTO customers (first_name, last_name, email, city, signup_date) VALUES
    ('Lucía',     'García',    'lucia.garcia@example.com',     'Alicante',  '2024-02-11'),
    ('Javier',    'Martínez',  'javier.martinez@example.com',  'Madrid',    '2024-03-05'),
    ('Carmen',    'López',     'carmen.lopez@example.com',     'Valencia',  '2024-04-19'),
    ('Pablo',     'Sánchez',   'pablo.sanchez@example.com',    'Alicante',  '2024-05-02'),
    ('Elena',     'Romero',    'elena.romero@example.com',     'Barcelona', '2024-06-23'),
    ('Diego',     'Navarro',   'diego.navarro@example.com',    'Sevilla',   '2024-07-14'),
    ('Laura',     'Torres',    'laura.torres@example.com',     'Elche',     '2024-08-30'),
    ('Sergio',    'Ruiz',      'sergio.ruiz@example.com',      'Madrid',    '2024-09-09'),
    ('Marta',     'Díaz',      'marta.diaz@example.com',       'Alicante',  '2024-10-17'),
    ('Andrés',    'Moreno',    'andres.moreno@example.com',    'Murcia',    '2024-11-21'),
    ('Paula',     'Jiménez',   'paula.jimenez@example.com',    'Valencia',  '2025-01-08'),
    ('Raúl',      'Herrera',   'raul.herrera@example.com',     'Bilbao',    '2025-02-14'),
    ('Sara',      'Molina',    'sara.molina@example.com',      'Alicante',  '2025-03-27'),
    ('Hugo',      'Ortega',    'hugo.ortega@example.com',      'Barcelona', '2025-05-06'),
    ('Irene',     'Castro',    'irene.castro@example.com',     'Elche',     '2025-06-15'),
    ('Álvaro',    'Vega',      'alvaro.vega@example.com',      'Madrid',    '2025-08-03'),
    ('Nuria',     'Ramos',     'nuria.ramos@example.com',      'Sevilla',   '2025-09-22'),
    ('Marcos',    'Gil',       'marcos.gil@example.com',       'Murcia',    '2025-11-11'),
    ('Claudia',   'Serrano',   'claudia.serrano@example.com',  'Valencia',  '2026-01-19'),
    ('Iván',      'Blanco',    'ivan.blanco@example.com',      'Alicante',  '2026-03-02');

INSERT INTO products (name, category_id, unit_price) VALUES
    -- Electronics (1)
    ('Wireless Headphones',   1,  79.99),
    ('Smartphone Case',       1,  15.50),
    ('USB-C Charger',         1,  24.90),
    ('Bluetooth Speaker',     1,  49.95),
    ('Smartwatch',            1, 199.00),
    -- Books (2)
    ('SQL for Beginners',     2,  29.90),
    ('Python Data Science',   2,  39.95),
    ('The Docker Book',       2,  34.50),
    ('Mystery Novel',         2,  12.99),
    -- Home (3)
    ('Coffee Maker',          3,  89.00),
    ('Desk Lamp',             3,  27.50),
    ('Cotton Bed Sheets',     3,  45.00),
    ('Kitchen Knife Set',     3,  64.90),
    -- Sports (4)
    ('Yoga Mat',              4,  22.00),
    ('Running Shoes',         4, 119.95),
    ('Dumbbell Set',          4,  74.50),
    ('Water Bottle',          4,   9.99),
    -- Clothing (5)
    ('Cotton T-Shirt',        5,  14.99),
    ('Denim Jeans',           5,  49.90),
    ('Rain Jacket',           5,  89.95);

-- Fixed seed: random() returns the same sequence on every run
SELECT setseed(0.42);

-- 200 orders spread over the last 365 days
INSERT INTO orders (customer_id, order_date, status)
SELECT
    1 + floor(random() * 20)::int                      AS customer_id,
    CURRENT_DATE - floor(random() * 365)::int          AS order_date,
    (ARRAY['delivered', 'delivered', 'delivered',
           'shipped', 'pending', 'cancelled'])[1 + floor(random() * 6)::int] AS status
FROM generate_series(1, 200);

-- 1 to 4 different products per order; the sale price is the
-- product price at the time (copied from products)
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.order_id, p.product_id, 1 + floor(random() * 3)::int, p.unit_price
FROM orders o
CROSS JOIN LATERAL (
    SELECT product_id, unit_price
    FROM products
    WHERE o.order_id > 0              -- makes the subquery run once per order
    ORDER BY random()
    LIMIT 1 + floor(random() * 4)::int
) p;
