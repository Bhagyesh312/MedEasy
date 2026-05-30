-- ============================================================
-- Migration: OTP verification table
-- Run this in pgAdmin4 after 03_add_users.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS otp_codes (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL,
    code        VARCHAR(6)   NOT NULL,
    purpose     VARCHAR(50)  NOT NULL DEFAULT 'register',  -- register | reset
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    expires_at  TIMESTAMP    NOT NULL,
    used        BOOLEAN      DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_otp_email   ON otp_codes(email);
CREATE INDEX IF NOT EXISTS idx_otp_expires ON otp_codes(expires_at);
