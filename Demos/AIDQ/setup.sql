USE ROLE ACCOUNTADMIN;
USE WAREHOUSE APP_WH;

CREATE SCHEMA IF NOT EXISTS TH_DEMO_DB.AIDQ_DEMO
COMMENT='Demo of AI-powered data quality suggestions';

USE DATABASE TH_DEMO_DB;
USE SCHEMA AIDQ_DEMO;

CREATE OR REPLACE TABLE BATCHES (
    BATCH_ID        INT PRIMARY KEY,
    BATCH_DATE      DATE NOT NULL,
    FACILITY_CODE   VARCHAR(10) NOT NULL
);

INSERT INTO BATCHES
SELECT
    SEQ4()                                                          AS BATCH_ID,
    DATEADD('day', -UNIFORM(0, 365, RANDOM()), CURRENT_DATE())     AS BATCH_DATE,
    'FAC-' || LPAD(UNIFORM(1, 5, RANDOM())::STRING, 3, '0')       AS FACILITY_CODE
FROM TABLE(GENERATOR(ROWCOUNT => 200));

CREATE OR REPLACE TABLE SHIPMENT_LOGS (
    SHIPMENT_ID         INT PRIMARY KEY,
    BATCH_ID            INT NOT NULL REFERENCES BATCHES(BATCH_ID),
    SHIP_DATE           DATE NOT NULL,
    DELIVERY_DATE       DATE,
    ORIGIN_REGION       VARCHAR(20) NOT NULL,
    DESTINATION_REGION  VARCHAR(20) NOT NULL,
    CARRIER             VARCHAR(30) NOT NULL,
    SHIPMENT_STATUS     VARCHAR(15) NOT NULL,
    PACKAGE_TYPE        VARCHAR(15) NOT NULL,
    WEIGHT_KG           NUMBER(10,2) NOT NULL,
    DECLARED_VALUE_USD  NUMBER(12,2),
    DISTANCE_KM         NUMBER(10,1),
    ITEMS_COUNT         INT NOT NULL
);

INSERT INTO SHIPMENT_LOGS
SELECT
    SEQ4()                                                              AS SHIPMENT_ID,
    UNIFORM(0, 199, RANDOM())                                          AS BATCH_ID,
    DATEADD('day', -UNIFORM(0, 365, RANDOM()), CURRENT_DATE())         AS SHIP_DATE,
    CASE
        WHEN UNIFORM(1, 100, RANDOM()) <= 85
        THEN DATEADD('day', UNIFORM(1, 30, RANDOM()), DATEADD('day', -UNIFORM(0, 365, RANDOM()), CURRENT_DATE()))
        ELSE NULL
    END                                                                 AS DELIVERY_DATE,
    ARRAY_CONSTRUCT(
        'North America', 'Europe', 'Asia Pacific',
        'Latin America', 'Middle East', 'Africa'
    )[UNIFORM(0, 5, RANDOM())]::VARCHAR                                 AS ORIGIN_REGION,
    ARRAY_CONSTRUCT(
        'North America', 'Europe', 'Asia Pacific',
        'Latin America', 'Middle East', 'Africa'
    )[UNIFORM(0, 5, RANDOM())]::VARCHAR                                 AS DESTINATION_REGION,
    ARRAY_CONSTRUCT(
        'FedEx', 'UPS', 'DHL', 'Maersk',
        'DB Schenker', 'XPO Logistics'
    )[UNIFORM(0, 5, RANDOM())]::VARCHAR                                 AS CARRIER,
    ARRAY_CONSTRUCT(
        'Delivered', 'In Transit', 'Pending',
        'Returned', 'Cancelled'
    )[UNIFORM(0, 4, RANDOM())]::VARCHAR                                 AS SHIPMENT_STATUS,
    ARRAY_CONSTRUCT(
        'Pallet', 'Parcel', 'Container',
        'Envelope', 'Crate'
    )[UNIFORM(0, 4, RANDOM())]::VARCHAR                                 AS PACKAGE_TYPE,
    ROUND(UNIFORM(0.5, 500.0, RANDOM())::NUMBER(10,2), 2)              AS WEIGHT_KG,
    ROUND(UNIFORM(10.0, 50000.0, RANDOM())::NUMBER(12,2), 2)           AS DECLARED_VALUE_USD,
    ROUND(UNIFORM(50.0, 15000.0, RANDOM())::NUMBER(10,1), 1)           AS DISTANCE_KM,
    UNIFORM(1, 200, RANDOM())                                           AS ITEMS_COUNT
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- ============================================================
-- INTRODUCE DATA QUALITY ISSUES
-- ============================================================

-- 1. Carrier: case errors and double spaces (~5% of rows each)
UPDATE SHIPMENT_LOGS
SET CARRIER = CASE UNIFORM(1, 4, RANDOM())
    WHEN 1 THEN UPPER(CARRIER)
    WHEN 2 THEN LOWER(CARRIER)
    WHEN 3 THEN REPLACE(CARRIER, ' ', '  ')
    ELSE LOWER(LEFT(CARRIER, 1)) || SUBSTR(CARRIER, 2)
END
WHERE UNIFORM(1, 100, RANDOM()) <= 10;

-- 2. Drop NOT NULL on region columns so we can inject nulls
ALTER TABLE SHIPMENT_LOGS ALTER COLUMN ORIGIN_REGION DROP NOT NULL;
ALTER TABLE SHIPMENT_LOGS ALTER COLUMN DESTINATION_REGION DROP NOT NULL;

UPDATE SHIPMENT_LOGS SET ORIGIN_REGION = NULL
WHERE UNIFORM(1, 100, RANDOM()) <= 2;

UPDATE SHIPMENT_LOGS SET DESTINATION_REGION = NULL
WHERE UNIFORM(1, 100, RANDOM()) <= 2;

-- 3. Zero distances (~3%)
UPDATE SHIPMENT_LOGS SET DISTANCE_KM = 0
WHERE UNIFORM(1, 100, RANDOM()) <= 3;

-- 4. Orphaned batch IDs (~2%)
UPDATE SHIPMENT_LOGS SET BATCH_ID = BATCH_ID + 10000
WHERE UNIFORM(1, 100, RANDOM()) <= 2;


/* Demo flow
1. Go to table in the UI
2. Navigate to the data quality tab
3. Take a look at the checks suggested by AI
4. Explore manual check assignment and creation
*/