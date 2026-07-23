-- Seed reference data: warehouse zones + item states.
-- From the WMS implementation plan §5.1 (zones) and §5.2 (states).

-- ──────────────────────────────────────────────────────────────────────
-- Zones (§5.1 of the plan)
-- ──────────────────────────────────────────────────────────────────────
INSERT INTO wms_zones (code, name_ru, zone_type, sort_order) VALUES
    ('RECEIVE',      'Приёмка',            'receive',    10),
    ('STORAGE',      'Основное хранение',  'storage',    20),
    ('PICK',         'Зона отбора',        'pick',       30),
    ('ASSEMBLY',     'Комплектация',       'pack',       40),
    ('PACK',         'Упаковка',           'pack',       50),
    ('READY_TO_SHIP','Готово к отгрузке',  'ship',       60),
    ('RETURNS',      'Возвраты',            'returns',    70),
    ('QUARANTINE',   'Карантин',            'quarantine', 80),
    ('DAMAGED',      'Брак',                'damage',     90),
    ('PRODUCTION',   'Производство',        'production', 100),
    ('TRANSIT',      'Товар в пути',        'transit',    110)
ON CONFLICT (code) DO NOTHING;

-- ──────────────────────────────────────────────────────────────────────
-- Item states (§5.2 of the plan)
-- ──────────────────────────────────────────────────────────────────────
INSERT INTO wms_item_states (state, name_ru, is_sellable, sort_order) VALUES
    ('SELLABLE',          'Доступен к продаже',     TRUE,  10),
    ('RESERVED',          'Зарезервирован',         FALSE, 20),
    ('PICKED',            'Отобран',                FALSE, 30),
    ('PACKED',            'Упакован',               FALSE, 40),
    ('IN_TRANSIT',        'В пути',                 FALSE, 50),
    ('RETURN_INSPECTION', 'Возврат на проверке',    FALSE, 60),
    ('QUARANTINE',        'Карантин',               FALSE, 70),
    ('DAMAGED',           'Брак',                   FALSE, 80),
    ('SCRAPPED',          'Списан',                 FALSE, 90)
ON CONFLICT (state) DO NOTHING;
