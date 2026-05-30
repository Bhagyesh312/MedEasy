-- ============================================================
-- Sample data for testing (optional)
-- Run this after 01_create_tables.sql
-- ============================================================

INSERT INTO reports (filename, patient_name, raw_text, is_scanned, summary, status)
VALUES (
    'sample_blood_test.pdf',
    'Test Patient',
    'Sample CBC report text',
    FALSE,
    'Most values are within normal range. Haemoglobin is slightly low and should be discussed with your doctor.',
    'analysed'
);

INSERT INTO findings (report_id, test_name, value, reference_range, status, explanation, action, is_flagged)
VALUES
    (1, 'Haemoglobin', '10.2 g/dL', '13.0 - 17.0 g/dL', 'Low',
     'Haemoglobin carries oxygen in your blood. Your level is below normal, which may cause tiredness.',
     'Discuss iron supplementation with your doctor.', TRUE),

    (1, 'WBC Count', '7.2 x10³/µL', '4.0 - 11.0 x10³/µL', 'Normal',
     'White blood cells fight infections. Your count is within the healthy range.',
     'No action needed.', FALSE),

    (1, 'Platelets', '220 x10³/µL', '150 - 400 x10³/µL', 'Normal',
     'Platelets help your blood clot. Your count is normal.',
     'No action needed.', FALSE);

INSERT INTO doctor_questions (report_id, question)
VALUES
    (1, 'What is causing my low haemoglobin?'),
    (1, 'Do I need iron supplements or dietary changes?'),
    (1, 'Should I get a follow-up test in a few weeks?');
