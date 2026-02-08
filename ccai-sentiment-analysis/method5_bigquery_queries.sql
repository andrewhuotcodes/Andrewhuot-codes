-- ==============================================================================
-- Method 5 (Part 2): BigQuery SQL Queries for Turn-by-Turn Sentiment Analysis
-- ==============================================================================
--
-- WHAT THIS IS:
--   A collection of ready-to-use SQL queries for analyzing CCAI Insights
--   data in BigQuery. Each query is standalone — copy/paste it into the
--   BigQuery console and run it.
--
-- HOW TO USE:
--   1. First run method5_bigquery_export.sh to export data to BigQuery
--   2. Open the BigQuery console:
--      https://console.cloud.google.com/bigquery
--   3. Copy any query below and paste it into the query editor
--   4. Replace YOUR_PROJECT_ID and YOUR_DATASET with your actual values
--   5. Click "Run"
--
-- IMPORTANT:
--   Replace these placeholders in EVERY query:
--     YOUR_PROJECT_ID  -> your actual GCP project ID
--     YOUR_DATASET     -> your BigQuery dataset name (default: ccai_insights_data)
--     YOUR_TABLE       -> your BigQuery table name (default: conversations)
--
-- ==============================================================================


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 1: Turn-by-Turn Sentiment for All Conversations                   ║
-- ║                                                                          ║
-- ║  Shows every individual turn with its sentiment score and a label.       ║
-- ║  This is the core query for turn-by-turn analysis.                       ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    s.speakerTag AS speaker_id,
    CASE
        WHEN s.speakerTag = 1 THEN 'CUSTOMER'
        WHEN s.speakerTag = 2 THEN 'AGENT'
        ELSE 'UNKNOWN'
    END AS speaker_role,
    s.text AS turn_text,
    s.sentimentScore AS sentiment_score,
    s.sentimentMagnitude AS sentiment_magnitude,
    -- Classify into human-readable labels
    CASE
        WHEN s.sentimentScore >= 0.75 THEN 'POSITIVE'
        WHEN s.sentimentScore >= 0.25 THEN 'SOMEWHAT_POSITIVE'
        WHEN s.sentimentScore >= -0.25 AND s.sentimentMagnitude > 0.5 THEN 'MIXED'
        WHEN s.sentimentScore >= -0.25 THEN 'NEUTRAL'
        WHEN s.sentimentScore >= -0.75 THEN 'SOMEWHAT_NEGATIVE'
        ELSE 'NEGATIVE'
    END AS sentiment_label,
    s.startOffsetNanos AS start_time_nanos,
    s.endOffsetNanos AS end_time_nanos
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
    UNNEST(sentences) AS s
ORDER BY
    conversationName,
    s.startOffsetNanos ASC;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 2: Customer-Only Turn-by-Turn Sentiment                           ║
-- ║                                                                          ║
-- ║  Same as Query 1 but filtered to only show customer turns.               ║
-- ║  (CX Insights primarily scores customer sentiment.)                      ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    ROW_NUMBER() OVER (
        PARTITION BY conversationName
        ORDER BY s.startOffsetNanos ASC
    ) AS customer_turn_number,
    s.text AS customer_statement,
    s.sentimentScore AS sentiment_score,
    s.sentimentMagnitude AS sentiment_magnitude,
    CASE
        WHEN s.sentimentScore >= 0.75 THEN 'POSITIVE'
        WHEN s.sentimentScore >= 0.25 THEN 'SOMEWHAT_POSITIVE'
        WHEN s.sentimentScore >= -0.25 AND s.sentimentMagnitude > 0.5 THEN 'MIXED'
        WHEN s.sentimentScore >= -0.25 THEN 'NEUTRAL'
        WHEN s.sentimentScore >= -0.75 THEN 'SOMEWHAT_NEGATIVE'
        ELSE 'NEGATIVE'
    END AS sentiment_label
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
    UNNEST(sentences) AS s
WHERE
    s.speakerTag = 1  -- Customer turns only
ORDER BY
    conversationName,
    s.startOffsetNanos ASC;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 3: Conversation-Level Sentiment Summary                           ║
-- ║                                                                          ║
-- ║  One row per conversation with overall customer + agent sentiment.       ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    clientSentimentScore AS customer_sentiment_score,
    clientSentimentMagnitude AS customer_sentiment_magnitude,
    clientSentimentRationale AS customer_sentiment_rationale,
    agentSentimentScore AS agent_sentiment_score,
    agentSentimentMagnitude AS agent_sentiment_magnitude,
    -- Overall customer sentiment category
    CASE
        WHEN clientSentimentScore >= 0.5 THEN 'POSITIVE'
        WHEN clientSentimentScore > -0.5 THEN 'NEUTRAL'
        ELSE 'NEGATIVE'
    END AS customer_sentiment_category,
    -- Overall agent sentiment category
    CASE
        WHEN agentSentimentScore >= 0.5 THEN 'POSITIVE'
        WHEN agentSentimentScore > -0.5 THEN 'NEUTRAL'
        ELSE 'NEGATIVE'
    END AS agent_sentiment_category
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`
ORDER BY
    clientSentimentScore ASC;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 4: Sentiment Distribution Dashboard                               ║
-- ║                                                                          ║
-- ║  Aggregate counts: how many conversations are positive/neutral/negative? ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    COUNT(*) AS total_conversations,
    COUNTIF(clientSentimentScore >= 0.5) AS positive_count,
    COUNTIF(clientSentimentScore BETWEEN -0.5 AND 0.5) AS neutral_count,
    COUNTIF(clientSentimentScore <= -0.5) AS negative_count,
    ROUND(COUNTIF(clientSentimentScore >= 0.5) * 100.0 / COUNT(*), 1) AS positive_pct,
    ROUND(COUNTIF(clientSentimentScore BETWEEN -0.5 AND 0.5) * 100.0 / COUNT(*), 1) AS neutral_pct,
    ROUND(COUNTIF(clientSentimentScore <= -0.5) * 100.0 / COUNT(*), 1) AS negative_pct,
    ROUND(AVG(clientSentimentScore), 3) AS avg_customer_sentiment,
    ROUND(AVG(agentSentimentScore), 3) AS avg_agent_sentiment
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 5: Sentiment Shift Detection (Negative -> Positive)               ║
-- ║                                                                          ║
-- ║  Find conversations where the customer started negative and ended        ║
-- ║  positive. These are successful resolution examples.                     ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

WITH customer_turns AS (
    SELECT
        conversationName,
        s.sentimentScore AS score,
        ROW_NUMBER() OVER (
            PARTITION BY conversationName
            ORDER BY s.startOffsetNanos ASC
        ) AS turn_number,
        ROW_NUMBER() OVER (
            PARTITION BY conversationName
            ORDER BY s.startOffsetNanos DESC
        ) AS reverse_turn_number
    FROM
        `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
        UNNEST(sentences) AS s
    WHERE
        s.speakerTag = 1  -- Customer only
),
first_last AS (
    SELECT
        conversationName,
        MAX(CASE WHEN turn_number = 1 THEN score END) AS first_turn_sentiment,
        MAX(CASE WHEN reverse_turn_number = 1 THEN score END) AS last_turn_sentiment
    FROM customer_turns
    GROUP BY conversationName
)
SELECT
    conversationName,
    ROUND(first_turn_sentiment, 2) AS opening_sentiment,
    ROUND(last_turn_sentiment, 2) AS closing_sentiment,
    ROUND(last_turn_sentiment - first_turn_sentiment, 2) AS sentiment_shift,
    CASE
        WHEN last_turn_sentiment - first_turn_sentiment > 0.5 THEN 'MAJOR_IMPROVEMENT'
        WHEN last_turn_sentiment - first_turn_sentiment > 0 THEN 'MINOR_IMPROVEMENT'
        WHEN last_turn_sentiment - first_turn_sentiment = 0 THEN 'NO_CHANGE'
        WHEN last_turn_sentiment - first_turn_sentiment > -0.5 THEN 'MINOR_DECLINE'
        ELSE 'MAJOR_DECLINE'
    END AS shift_category
FROM first_last
WHERE
    first_turn_sentiment < 0          -- Started negative
    AND last_turn_sentiment > 0       -- Ended positive
ORDER BY
    sentiment_shift DESC;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 6: Most Negative Customer Moments                                 ║
-- ║                                                                          ║
-- ║  Find the most negative things customers said across all conversations.  ║
-- ║  Useful for identifying pain points and common complaints.               ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    s.text AS customer_statement,
    s.sentimentScore AS sentiment_score,
    s.sentimentMagnitude AS sentiment_magnitude,
    CASE
        WHEN s.sentimentScore <= -0.75 THEN 'VERY_NEGATIVE'
        WHEN s.sentimentScore <= -0.5 THEN 'NEGATIVE'
        ELSE 'SOMEWHAT_NEGATIVE'
    END AS severity
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
    UNNEST(sentences) AS s
WHERE
    s.speakerTag = 1                  -- Customer only
    AND s.sentimentScore <= -0.25     -- Negative or somewhat negative
ORDER BY
    s.sentimentScore ASC,
    s.sentimentMagnitude DESC
LIMIT 100;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 7: Most Positive Customer Moments                                 ║
-- ║                                                                          ║
-- ║  Find the most positive things customers said. Useful for identifying    ║
-- ║  what makes customers happy and training examples.                       ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    s.text AS customer_statement,
    s.sentimentScore AS sentiment_score,
    s.sentimentMagnitude AS sentiment_magnitude
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
    UNNEST(sentences) AS s
WHERE
    s.speakerTag = 1                  -- Customer only
    AND s.sentimentScore >= 0.25      -- Positive or somewhat positive
ORDER BY
    s.sentimentScore DESC,
    s.sentimentMagnitude DESC
LIMIT 100;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 8: Turn-by-Turn Sentiment Trend Within a Conversation             ║
-- ║                                                                          ║
-- ║  Shows how sentiment evolves turn by turn within each conversation.      ║
-- ║  Includes a running average for smoothing.                               ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    ROW_NUMBER() OVER (
        PARTITION BY conversationName
        ORDER BY s.startOffsetNanos ASC
    ) AS turn_number,
    CASE
        WHEN s.speakerTag = 1 THEN 'CUSTOMER'
        WHEN s.speakerTag = 2 THEN 'AGENT'
        ELSE 'UNKNOWN'
    END AS speaker,
    LEFT(s.text, 80) AS turn_text_preview,
    ROUND(s.sentimentScore, 2) AS sentiment_score,
    -- Running average of sentiment (last 3 turns for this speaker)
    ROUND(AVG(s.sentimentScore) OVER (
        PARTITION BY conversationName, s.speakerTag
        ORDER BY s.startOffsetNanos ASC
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_avg_sentiment_3turn
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
    UNNEST(sentences) AS s
ORDER BY
    conversationName,
    s.startOffsetNanos ASC;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 9: Entity Sentiment Analysis                                      ║
-- ║                                                                          ║
-- ║  See which entities (products, services, people) have positive or        ║
-- ║  negative sentiment associated with them.                                ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

SELECT
    conversationName,
    e.name AS entity_name,
    e.type AS entity_type,
    e.sentimentScore AS entity_sentiment_score,
    e.sentimentMagnitude AS entity_sentiment_magnitude,
    CASE
        WHEN e.sentimentScore >= 0.25 THEN 'POSITIVE'
        WHEN e.sentimentScore > -0.25 THEN 'NEUTRAL'
        ELSE 'NEGATIVE'
    END AS entity_sentiment_label
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
    UNNEST(entities) AS e
WHERE
    e.sentimentScore IS NOT NULL
ORDER BY
    ABS(e.sentimentScore) DESC
LIMIT 200;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║  QUERY 10: Complete Conversation Report (All Features)                   ║
-- ║                                                                          ║
-- ║  A comprehensive one-row-per-conversation summary combining sentiment,   ║
-- ║  entity count, turn count, and sentiment shift metrics.                  ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

WITH turn_stats AS (
    SELECT
        conversationName,
        COUNT(*) AS total_turns,
        COUNTIF(s.speakerTag = 1) AS customer_turns,
        COUNTIF(s.speakerTag = 2) AS agent_turns,
        -- Customer turn sentiments
        ROUND(AVG(CASE WHEN s.speakerTag = 1 THEN s.sentimentScore END), 3) AS avg_customer_turn_sentiment,
        ROUND(MIN(CASE WHEN s.speakerTag = 1 THEN s.sentimentScore END), 3) AS min_customer_sentiment,
        ROUND(MAX(CASE WHEN s.speakerTag = 1 THEN s.sentimentScore END), 3) AS max_customer_sentiment,
        -- Sentiment standard deviation (how volatile is the customer?)
        ROUND(STDDEV(CASE WHEN s.speakerTag = 1 THEN s.sentimentScore END), 3) AS customer_sentiment_volatility
    FROM
        `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
        UNNEST(sentences) AS s
    GROUP BY conversationName
),
entity_stats AS (
    SELECT
        conversationName,
        COUNT(*) AS entity_count
    FROM
        `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE`,
        UNNEST(entities) AS e
    GROUP BY conversationName
)
SELECT
    c.conversationName,
    -- Conversation-level sentiment
    ROUND(c.clientSentimentScore, 3) AS customer_sentiment,
    ROUND(c.agentSentimentScore, 3) AS agent_sentiment,
    c.clientSentimentRationale AS sentiment_rationale,
    -- Turn statistics
    ts.total_turns,
    ts.customer_turns,
    ts.agent_turns,
    -- Turn-level sentiment stats
    ts.avg_customer_turn_sentiment,
    ts.min_customer_sentiment,
    ts.max_customer_sentiment,
    ts.customer_sentiment_volatility,
    -- Sentiment range (max - min = how much emotion swung)
    ROUND(ts.max_customer_sentiment - ts.min_customer_sentiment, 3) AS sentiment_range,
    -- Entity count
    COALESCE(es.entity_count, 0) AS entities_found,
    -- Classification
    CASE
        WHEN c.clientSentimentScore >= 0.5 THEN 'POSITIVE'
        WHEN c.clientSentimentScore > -0.5 THEN 'NEUTRAL'
        ELSE 'NEGATIVE'
    END AS overall_classification
FROM
    `YOUR_PROJECT_ID.YOUR_DATASET.YOUR_TABLE` c
LEFT JOIN turn_stats ts ON c.conversationName = ts.conversationName
LEFT JOIN entity_stats es ON c.conversationName = es.conversationName
ORDER BY
    c.clientSentimentScore ASC;
