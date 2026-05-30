-- ============================================================
-- Migration: Add richer finding detail columns
-- Run this in pgAdmin4 / Neon SQL Editor
-- ============================================================

ALTER TABLE findings
  ADD COLUMN IF NOT EXISTS what_it_measures    TEXT,
  ADD COLUMN IF NOT EXISTS your_number_context VARCHAR(255),
  ADD COLUMN IF NOT EXISTS symptoms            TEXT,   -- stored as JSON array string
  ADD COLUMN IF NOT EXISTS urgency             VARCHAR(50) DEFAULT 'Routine',
  ADD COLUMN IF NOT EXISTS likely_next_step    TEXT;
