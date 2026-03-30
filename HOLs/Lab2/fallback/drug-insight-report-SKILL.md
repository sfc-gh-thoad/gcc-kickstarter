---
name: drug-insight-report
description: "Generate an executive drug insight report for a given compound. Use when: user asks for a drug report, compound analysis, drug summary, pipeline insight, or risk assessment for a specific compound name."
tools: ["snowflake_sql_execute"]
---

# Drug Insight Report

Generate a comprehensive executive summary for a pharmaceutical compound using live data and Cortex AI.

## Workflow

1. Look up the compound in `GSK_GCC_HOL.HOL_2.COMPOUNDS` by name
2. Pull all clinical trials for that compound from `CLINICAL_TRIALS`
3. Pull all adverse events from `ADVERSE_EVENTS` for those trials
4. Build a data summary with:
   - Compound details (therapeutic area, phase, target protein, biologic status)
   - Trial overview (phases, status, countries, total enrolled patients, success/failure)
   - Adverse event profile (counts by severity, most common event types, any fatal outcomes)
5. Pass the data summary to Cortex COMPLETE to generate a plain-English executive report covering:
   - **Pipeline Status**: Where is this compound in development?
   - **Efficacy Signal**: What do the trial results suggest?
   - **Safety Profile**: What adverse events have been observed and how severe?
   - **Risk Assessment**: Overall risk/benefit summary with recommendation

## SQL Template

```sql
USE WAREHOUSE COMPUTE_WH;

WITH compound_info AS (
    SELECT * FROM GSK_GCC_HOL.HOL_2.COMPOUNDS
    WHERE LOWER(compound_name) = LOWER('<COMPOUND_NAME>')
),
trial_info AS (
    SELECT t.*
    FROM GSK_GCC_HOL.HOL_2.CLINICAL_TRIALS t
    JOIN compound_info c ON t.compound_id = c.compound_id
),
ae_info AS (
    SELECT a.*
    FROM GSK_GCC_HOL.HOL_2.ADVERSE_EVENTS a
    JOIN trial_info t ON a.trial_id = t.trial_id
),
data_summary AS (
    SELECT OBJECT_CONSTRUCT(
        'compound', (SELECT compound_name FROM compound_info),
        'therapeutic_area', (SELECT therapeutic_area FROM compound_info),
        'phase', (SELECT phase FROM compound_info),
        'target_protein', (SELECT target_protein FROM compound_info),
        'is_biologic', (SELECT is_biologic FROM compound_info),
        'trials', (SELECT COUNT(*) FROM trial_info),
        'total_enrolled', (SELECT SUM(enrolled_patients) FROM trial_info),
        'completed_trials', (SELECT COUNT(*) FROM trial_info WHERE status = 'Completed'),
        'successful_trials', (SELECT COUNT(*) FROM trial_info WHERE success = TRUE),
        'active_trials', (SELECT COUNT(*) FROM trial_info WHERE status = 'Active'),
        'countries', (SELECT ARRAY_AGG(DISTINCT site_country) FROM trial_info),
        'total_adverse_events', (SELECT COUNT(*) FROM ae_info),
        'severe_events', (SELECT COUNT(*) FROM ae_info WHERE severity = 'Severe'),
        'fatal_outcomes', (SELECT COUNT(*) FROM ae_info WHERE outcome = 'Fatal'),
        'top_event_types', (SELECT ARRAY_AGG(DISTINCT event_type) FROM ae_info)
    ) AS summary
)
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-70b',
    'You are a pharmaceutical analyst. Based on this clinical data, write a concise executive insight report with sections: Pipeline Status, Efficacy Signal, Safety Profile, and Risk Assessment. Data: ' || summary::VARCHAR
) AS insight_report
FROM data_summary;
```

## Stopping Points
- If compound not found, inform the user and list available compounds
- If no trials exist for the compound, report that and skip efficacy/safety sections
