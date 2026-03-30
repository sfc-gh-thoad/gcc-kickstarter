USE DATABASE HOL_2_WORK;
USE SCHEMA HOL_2;
USE WAREHOUSE COMPUTE_WH;

CREATE OR REPLACE TABLE PATIENT_DEMOGRAPHICS AS
WITH trial_pool AS (
    SELECT trial_id, start_date,
        COALESCE(end_date, '2025-12-31'::DATE) AS eff_end,
        DATEDIFF('day', start_date, COALESCE(end_date, '2025-12-31'::DATE)) AS day_range
    FROM GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS
),
generated AS (
    SELECT
        tp.trial_id,
        tp.start_date,
        tp.day_range,
        ROW_NUMBER() OVER (ORDER BY RANDOM()) AS rn
    FROM trial_pool tp,
        TABLE(GENERATOR(ROWCOUNT => 2000)) g
)
SELECT
    'PT-' || (20000 + rn) AS patient_id,
    trial_id,
    UNIFORM(22, 78, RANDOM()) AS age,
    CASE WHEN UNIFORM(0, 1, RANDOM()) = 0 THEN 'Male' ELSE 'Female' END AS sex,
    CASE UNIFORM(1, 6, RANDOM())
        WHEN 1 THEN 'White' WHEN 2 THEN 'Black or African American'
        WHEN 3 THEN 'Asian' WHEN 4 THEN 'Hispanic or Latino'
        WHEN 5 THEN 'South Asian' ELSE 'Other'
    END AS ethnicity,
    ROUND(UNIFORM(18.0::FLOAT, 42.0::FLOAT, RANDOM()), 1) AS bmi,
    CASE UNIFORM(1, 4, RANDOM())
        WHEN 1 THEN 'Never' WHEN 2 THEN 'Former'
        WHEN 3 THEN 'Current' ELSE 'Unknown'
    END AS smoker_status,
    CASE UNIFORM(1, 8, RANDOM())
        WHEN 1 THEN 'None' WHEN 2 THEN 'Hypertension'
        WHEN 3 THEN 'Diabetes Type 2' WHEN 4 THEN 'Asthma'
        WHEN 5 THEN 'Obesity' WHEN 6 THEN 'Hypertension, Diabetes Type 2'
        WHEN 7 THEN 'Cardiovascular Disease' ELSE 'Chronic Kidney Disease'
    END AS comorbidities,
    DATEADD('day', MOD(ABS(RANDOM()), GREATEST(day_range, 1)), start_date) AS enrollment_date
FROM generated
WHERE rn <= 200;

SELECT COUNT(*) AS total_patients FROM PATIENT_DEMOGRAPHICS;
