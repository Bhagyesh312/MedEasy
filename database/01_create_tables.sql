-- ============================================================
-- Medical Report Simplifier — Database Schema
-- Run this file first in pgAdmin4
-- ============================================================

-- Create database (run this separately if needed)
-- CREATE DATABASE medical_report_db;

-- ============================================================
-- Table: reports
-- Stores each uploaded report and its analysis
-- ============================================================
CREATE TABLE IF NOT EXISTS reports (
    id              SERIAL PRIMARY KEY,
    filename        VARCHAR(255) NOT NULL,
    patient_name    VARCHAR(255),
    uploaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_text        TEXT,
    is_scanned      BOOLEAN DEFAULT FALSE,
    summary         TEXT,
    status          VARCHAR(50) DEFAULT 'pending'  -- pending | analysed | error
);

-- ============================================================
-- Table: findings
-- Each individual test result from a report
-- ============================================================
CREATE TABLE IF NOT EXISTS findings (
    id              SERIAL PRIMARY KEY,
    report_id       INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    test_name       VARCHAR(255) NOT NULL,
    value           VARCHAR(255),
    reference_range VARCHAR(255),
    status          VARCHAR(50),   -- Normal | High | Low | Critical | Unknown
    explanation     TEXT,
    action          TEXT,
    is_flagged      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: doctor_questions
-- Questions generated for the patient to ask their doctor
-- ============================================================
CREATE TABLE IF NOT EXISTS doctor_questions (
    id              SERIAL PRIMARY KEY,
    report_id       INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    question        TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Indexes for faster queries
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_findings_report_id ON findings(report_id);
CREATE INDEX IF NOT EXISTS idx_findings_is_flagged ON findings(is_flagged);
CREATE INDEX IF NOT EXISTS idx_doctor_questions_report_id ON doctor_questions(report_id);
CREATE INDEX IF NOT EXISTS idx_reports_uploaded_at ON reports(uploaded_at DESC);
