-- Pharma Pipeline Performance Report
-- "Complicated" query with plenty of optimisation opportunities

WITH RECURSIVE date_spine AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM date_spine WHERE n < 50
),
exploded_sales AS (
    SELECT s.*, d.n AS dummy_row
    FROM GSK_GCC_HOL.HOL_2.SALES_DATA s
    CROSS JOIN date_spine d
),
exploded_compounds AS (
    SELECT c.*, d.n AS dummy_row
    FROM GSK_GCC_HOL.HOL_2.COMPOUNDS c
    CROSS JOIN date_spine d
    WHERE d.n <= 5
),
ae_verbose AS (
    SELECT
        ae1.TRIAL_ID,
        ae1.EVENT_ID,
        ae1.SEVERITY,
        ae2.EVENT_TYPE AS related_event_type,
        ae2.OUTCOME AS related_outcome,
        CASE WHEN ae1.SEVERITY = ae2.SEVERITY THEN 1 ELSE 0 END AS severity_match
    FROM GSK_GCC_HOL.HOL_2.ADVERSE_EVENTS ae1
    CROSS JOIN GSK_GCC_HOL.HOL_2.ADVERSE_EVENTS ae2
    CROSS JOIN date_spine d
),
ae_stats AS (
    SELECT
        TRIAL_ID,
        COUNT(*) AS adverse_event_count,
        SUM(CASE WHEN SEVERITY = 'Severe' THEN 1 ELSE 0 END) AS severe_count,
        ROUND(SUM(CASE WHEN SEVERITY = 'Severe' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_severe,
        SUM(severity_match) AS useless_metric
    FROM ae_verbose
    GROUP BY TRIAL_ID
),
pd_bloated AS (
    SELECT
        pd1.TRIAL_ID,
        pd1.PATIENT_ID,
        pd1.AGE,
        pd1.SMOKER_STATUS,
        pd2.BMI AS other_bmi,
        pd2.SEX AS other_sex,
        ABS(pd1.AGE - pd2.AGE) AS age_diff
    FROM HOL_2_WORK.HOL_2.PATIENT_DEMOGRAPHICS pd1
    CROSS JOIN HOL_2_WORK.HOL_2.PATIENT_DEMOGRAPHICS pd2
    CROSS JOIN date_spine d
),
pd_stats AS (
    SELECT
        TRIAL_ID,
        AVG(AGE) AS avg_patient_age,
        COUNT(*) AS total_patients_enrolled,
        SUM(CASE WHEN SMOKER_STATUS = 'Current' THEN 1 ELSE 0 END) AS smoker_count,
        AVG(age_diff) AS avg_age_diff_useless
    FROM pd_bloated
    GROUP BY TRIAL_ID
),
massive_join AS (
    SELECT
        ec.COMPOUND_NAME,
        ec.THERAPEUTIC_AREA,
        ec.IS_BIOLOGIC,
        ec.MOLECULAR_WEIGHT,
        es.REGION,
        es.YEAR,
        es.QUARTER,
        es.CHANNEL,
        es.REVENUE_USD,
        es.UNITS_SOLD,
        (SELECT AVG(REVENUE_USD) FROM GSK_GCC_HOL.HOL_2.SALES_DATA) AS global_avg_revenue,
        (SELECT COUNT(*) FROM GSK_GCC_HOL.HOL_2.ADVERSE_EVENTS WHERE SEVERITY = 'Severe') AS total_severe_events,
        (SELECT MAX(MOLECULAR_WEIGHT) FROM GSK_GCC_HOL.HOL_2.COMPOUNDS) AS max_mol_weight,
        (SELECT COUNT(DISTINCT TRIAL_PHASE) FROM GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS) AS distinct_phases,
        ct.TRIAL_PHASE,
        ct.STATUS AS trial_status,
        ct.ENROLLED_PATIENTS,
        ct.SUCCESS AS trial_success,
        ct.SITE_COUNTRY,
        ae_stats.adverse_event_count,
        ae_stats.severe_count,
        ae_stats.pct_severe,
        ae_stats.useless_metric,
        pd_stats.avg_patient_age,
        pd_stats.total_patients_enrolled,
        pd_stats.smoker_count,
        pd_stats.avg_age_diff_useless,
        MD5(ec.COMPOUND_NAME || es.REGION || es.QUARTER || CAST(es.YEAR AS VARCHAR)) AS row_hash,
        LENGTH(ec.COMPOUND_NAME) * ec.MOLECULAR_WEIGHT AS pointless_calc
    FROM exploded_sales es
    CROSS JOIN exploded_compounds ec
    LEFT JOIN GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS ct
        ON ct.COMPOUND_ID = ec.COMPOUND_ID
    LEFT JOIN ae_stats ON ae_stats.TRIAL_ID = ct.TRIAL_ID
    LEFT JOIN pd_stats ON pd_stats.TRIAL_ID = ct.TRIAL_ID
    WHERE es.YEAR >= 2020
),
aggregated AS (
    SELECT
        COMPOUND_NAME,
        THERAPEUTIC_AREA,
        IS_BIOLOGIC,
        MOLECULAR_WEIGHT,
        REGION,
        YEAR,
        QUARTER,
        CHANNEL,
        SUM(REVENUE_USD) AS total_revenue,
        SUM(UNITS_SOLD) AS total_units,
        ROUND(SUM(REVENUE_USD) / NULLIF(SUM(UNITS_SOLD), 0), 2) AS avg_price_per_unit,
        MAX(global_avg_revenue) AS global_avg_revenue,
        MAX(total_severe_events) AS total_severe_events,
        MAX(max_mol_weight) AS max_mol_weight,
        MAX(distinct_phases) AS distinct_phases,
        TRIAL_PHASE,
        trial_status,
        ENROLLED_PATIENTS,
        trial_success,
        SITE_COUNTRY,
        MAX(adverse_event_count) AS adverse_event_count,
        MAX(severe_count) AS severe_count,
        MAX(pct_severe) AS pct_severe,
        MAX(useless_metric) AS useless_metric,
        MAX(avg_patient_age) AS avg_patient_age,
        MAX(total_patients_enrolled) AS total_patients_enrolled,
        MAX(smoker_count) AS smoker_count,
        MAX(avg_age_diff_useless) AS avg_age_diff_useless,
        MAX(row_hash) AS sample_hash,
        AVG(pointless_calc) AS avg_pointless,
        CASE
            WHEN SUM(REVENUE_USD) > 500000 THEN 'High Performer'
            WHEN SUM(REVENUE_USD) > 100000 THEN 'Mid Performer'
            ELSE 'Low Performer'
        END AS performance_tier
    FROM massive_join
    GROUP BY
        COMPOUND_NAME, THERAPEUTIC_AREA, IS_BIOLOGIC, MOLECULAR_WEIGHT,
        REGION, YEAR, QUARTER, CHANNEL,
        TRIAL_PHASE, trial_status, ENROLLED_PATIENTS, trial_success, SITE_COUNTRY
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY COMPOUND_NAME ORDER BY total_revenue DESC) AS rn,
        RANK() OVER (PARTITION BY REGION ORDER BY total_revenue DESC) AS region_rank,
        DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS overall_rank,
        LAG(total_revenue) OVER (PARTITION BY COMPOUND_NAME ORDER BY YEAR, QUARTER) AS prev_revenue,
        LEAD(total_revenue) OVER (PARTITION BY COMPOUND_NAME ORDER BY YEAR, QUARTER) AS next_revenue,
        SUM(total_revenue) OVER (PARTITION BY COMPOUND_NAME ORDER BY YEAR, QUARTER ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        AVG(total_revenue) OVER (PARTITION BY REGION) AS avg_region_revenue
    FROM aggregated
)
SELECT * FROM ranked
WHERE total_revenue > 0
ORDER BY total_revenue DESC, COMPOUND_NAME;
