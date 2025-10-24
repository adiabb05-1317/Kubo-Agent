-- seed_data.sql
-- Populates the users, pods, and bookings tables with sample records.

-- Users ---------------------------------------------------------------------
INSERT INTO users (email, full_name, hashed_password, is_admin, is_active)
VALUES
  ('admin@example.com', 'Admin User', '$2b$12$9C0Vx1j7YI/6O0q4Gyk0GeSBylWb1N1F.8Ey96VEh9UpAJZciV06S', TRUE, TRUE),
  ('manager@example.com', 'Manager User', '$2b$12$P8cGZr5n4zsP/D6.YB2SgO5Z1PFsKnz03Wx/ju0RduCMsZ/HXXIQK', TRUE, TRUE),
  ('guest@example.com', 'Guest User', '$2b$12$4PNleVulYx.MR.cI43cbk.zY6z3Y0JVpaz6RtWLpmjHtkobaN6D2K', FALSE, TRUE)
ON CONFLICT (email) DO UPDATE
SET full_name = EXCLUDED.full_name,
    hashed_password = EXCLUDED.hashed_password,
    is_admin = EXCLUDED.is_admin,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;


-- Pods ----------------------------------------------------------------------
INSERT INTO pods (name, description, capacity, price_cents, is_active)
VALUES
  ('Serenity Suite', 'Premium two-person pod with ambient lighting and acoustic isolation.', 2, 12500, TRUE),
  ('Focus Hub', 'Solo productivity pod with height-adjustable desk and ergonomic chair.', 1, 8500, TRUE),
  ('Collaboration Cove', 'Small team pod with whiteboard walls and shared screens.', 4, 15500, TRUE),
  ('Zen Den', 'Meditative pod with reclining seat and calming soundscape.', 1, 7200, TRUE),
  ('Skyline Retreat', 'Corner pod with panoramic city views and natural light.', 2, 14200, TRUE),
  ('Horizon Pod', 'Convertible standing/sitting workspace with AR display.', 1, 9800, TRUE),
  ('Harbor Workspace', 'Dual workstation pod overlooking the atrium.', 2, 11300, TRUE),
  ('Innovation Nook', 'Brainstorm pod stocked with digital sketch tools.', 3, 13200, TRUE),
  ('Summit Capsule', 'Executive pod with concierge support and premium coffee.', 2, 16800, TRUE),
  ('Aurora Lounge', 'Relaxed collaboration lounge with sofa seating and projector.', 5, 14900, TRUE)
ON CONFLICT (name) DO UPDATE
SET description = EXCLUDED.description,
    capacity = EXCLUDED.capacity,
    price_cents = EXCLUDED.price_cents,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;


-- Bookings ------------------------------------------------------------------
-- Booking 1: Admin books Serenity Suite for tomorrow.
WITH selected_user AS (
  SELECT id AS user_id FROM users WHERE email = 'admin@example.com'
),
selected_pod AS (
  SELECT id AS pod_id, price_cents FROM pods WHERE name = 'Serenity Suite'
)
INSERT INTO bookings (user_id, pod_id, start_time, end_time, status, total_price_cents, guests)
SELECT
  su.user_id,
  sp.pod_id,
  (NOW() AT TIME ZONE 'UTC') + INTERVAL '1 day' AS start_time,
  (NOW() AT TIME ZONE 'UTC') + INTERVAL '1 day 2 hours' AS end_time,
  'confirmed',
  sp.price_cents,
  '[{"name": "Jess", "email": "jess@example.com"}, {"name": "Ravi", "email": "ravi@example.com"}]'::jsonb
FROM selected_user su
JOIN selected_pod sp ON TRUE
ON CONFLICT (pod_id, start_time, end_time) DO UPDATE
SET status = EXCLUDED.status,
    total_price_cents = EXCLUDED.total_price_cents,
    updated_at = CURRENT_TIMESTAMP;

-- Booking 2: Guest books Focus Hub for the day after tomorrow.
WITH selected_user AS (
  SELECT id AS user_id FROM users WHERE email = 'guest@example.com'
),
selected_pod AS (
  SELECT id AS pod_id, price_cents FROM pods WHERE name = 'Focus Hub'
)
INSERT INTO bookings (user_id, pod_id, start_time, end_time, status, total_price_cents, guests)
SELECT
  su.user_id,
  sp.pod_id,
  (NOW() AT TIME ZONE 'UTC') + INTERVAL '2 day' AS start_time,
  (NOW() AT TIME ZONE 'UTC') + INTERVAL '2 day 1 hour' AS end_time,
  'confirmed',
  sp.price_cents,
  '[{"name": "Lara", "email": "lara@example.com"}]'::jsonb
FROM selected_user su
JOIN selected_pod sp ON TRUE
ON CONFLICT (pod_id, start_time, end_time) DO UPDATE
SET status = EXCLUDED.status,
    total_price_cents = EXCLUDED.total_price_cents,
    updated_at = CURRENT_TIMESTAMP;


