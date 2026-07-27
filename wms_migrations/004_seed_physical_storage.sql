-- Physical address-storage layout imported from the existing MoySklad labels.
-- The printed Code 128 payload is the location code itself (without LOC:), so
-- code and barcode intentionally remain identical.

INSERT INTO wms_zones (code, name_ru, zone_type, sort_order) VALUES
    ('Z1', 'Зона №1', 'storage', 21),
    ('Z2', 'Зона №2', 'storage', 22),
    ('Z3', 'Зона №3', 'storage', 23),
    ('Z4', 'Зона №4', 'storage', 24)
ON CONFLICT (code) DO UPDATE SET
    name_ru = EXCLUDED.name_ru,
    zone_type = EXCLUDED.zone_type,
    sort_order = EXCLUDED.sort_order,
    is_active = TRUE;

WITH desired_cells AS (
    SELECT
        zone_no,
        section_no,
        shelf_no,
        position_no,
        format('Z%s-S%s-P%s-%s', zone_no, section_no, shelf_no, position_no) AS cell_code
    FROM generate_series(1, 4) AS zone_no
    CROSS JOIN generate_series(1, 5) AS section_no
    CROSS JOIN generate_series(1, 3) AS shelf_no
    CROSS JOIN generate_series(1, 2) AS position_no
    WHERE (zone_no <= 3 AND section_no <= 5)
       OR (zone_no = 4 AND section_no <= 2)
)
INSERT INTO wms_locations (
    zone_id,
    code,
    barcode,
    name_ru,
    pick_priority,
    route_order,
    status
)
SELECT
    zones.id,
    cells.cell_code,
    cells.cell_code,
    format('Ячейка %s', cells.cell_code),
    (cells.zone_no * 1000) + (cells.section_no * 100) + (cells.shelf_no * 10) + cells.position_no,
    (cells.zone_no * 1000) + (cells.section_no * 100) + (cells.shelf_no * 10) + cells.position_no,
    'active'
FROM desired_cells AS cells
JOIN wms_zones AS zones ON zones.code = format('Z%s', cells.zone_no)
ON CONFLICT (code) DO UPDATE SET
    zone_id = EXCLUDED.zone_id,
    barcode = EXCLUDED.barcode,
    name_ru = EXCLUDED.name_ru,
    pick_priority = EXCLUDED.pick_priority,
    route_order = EXCLUDED.route_order,
    status = 'active';
