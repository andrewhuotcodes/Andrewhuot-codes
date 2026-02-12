# PRD-027: BigQuery Analytics Export

**Phase:** 3 — "Make It Scale" | **Priority:** P1 | **Quarter:** Q1-Q2 2027
**Pillar:** Analytics | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Commerce Funnel Analytics dashboard (PRD-023) provides built-in analytics. But enterprise customers have existing BI infrastructure — Looker, Tableau, Power BI, custom data warehouses — and need raw event data in a format they can query, join with other data sources, and build custom models on.

BigQuery Analytics Export streams raw SDK events to the customer's BigQuery dataset in near real-time, enabling custom analysis, ML model training, and integration with existing data pipelines.

---

## What Are We Building

### Streaming Export Pipeline

```
Event Bus → Analytics Collector → Batch Buffer (10s / 100 events)
    → BigQuery Streaming Insert → Customer's BigQuery Dataset
```

### BigQuery Table Schema

```sql
CREATE TABLE `project.dataset.chat_sdk_events` (
  event_id STRING NOT NULL,          -- UUIDv7
  event_type STRING NOT NULL,        -- e.g., 'commerce:payment-completed'
  timestamp TIMESTAMP NOT NULL,
  session_id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  user_id_hash STRING,               -- pseudonymized
  agent_id STRING,
  agent_role STRING,
  source STRING,                     -- user, agent, system, widget, commerce
  payload JSON,                      -- full event payload
  -- Commerce-specific columns (denormalized for query performance)
  commerce_merchant_id STRING,
  commerce_order_id STRING,
  commerce_amount_cents INT64,
  commerce_currency STRING,
  -- Widget-specific
  widget_type STRING,
  widget_instance_id STRING,
  -- Metadata
  sdk_version STRING,
  platform STRING,                   -- web, ios, android
  locale STRING,
  viewport STRING,                   -- mobile, tablet, desktop
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, session_id;
```

### Configuration

```typescript
const config: ChatSDKConfig = {
  // ... other config
  analytics: {
    bigquery: {
      projectId: 'customer-project',
      datasetId: 'chat_analytics',
      tableId: 'chat_sdk_events',
      // Service account credentials are configured server-side
    },
    // Events to export (default: all)
    exportFilter: ['commerce:*', 'session:*', 'message:sent', 'message:received'],
    // Batch settings
    batchSize: 100,
    flushIntervalMs: 10000,
  },
};
```

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Export adoption | >30% of enterprise deployments enable BigQuery export | Configuration tracking |
| Data latency | <30 seconds from event to queryable in BigQuery | Timestamp comparison |
| Data completeness | >99.9% of events exported (no data loss) | Reconciliation with audit trail |
| Query performance | P95 <5s for daily aggregation queries | BigQuery monitoring |

### Success Criteria

1. A data analyst can write a BigQuery SQL query that joins chat SDK events with their existing sales data to calculate chat-attributed revenue.
2. Event data appears in BigQuery within 30 seconds of occurrence.
3. Data loss rate is <0.1% under normal operation.

---

## Critical User Journeys

### CUJ 1: Custom Revenue Attribution
**Actor:** Data analyst at a retailer
**Goal:** Calculate what percentage of revenue was influenced by the chat agent

```sql
SELECT
  DATE(timestamp) as date,
  COUNT(DISTINCT session_id) as chat_sessions,
  COUNTIF(event_type = 'commerce:payment-completed') as purchases,
  SUM(commerce_amount_cents) / 100.0 as total_gmv
FROM `project.chat_analytics.chat_sdk_events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY date
ORDER BY date DESC;
```

### CUJ 2: Agent Performance Comparison
**Actor:** Product manager optimizing agent configuration
**Goal:** Compare conversion rates across different agent configurations

```sql
SELECT
  agent_id,
  COUNT(DISTINCT session_id) as sessions,
  COUNTIF(event_type = 'commerce:cart-updated') / COUNT(DISTINCT session_id) as cart_rate,
  COUNTIF(event_type = 'commerce:payment-completed') / COUNT(DISTINCT session_id) as purchase_rate
FROM `project.chat_analytics.chat_sdk_events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY agent_id;
```

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Stream SDK events to customer's BigQuery dataset via streaming insert | P0 |
| FR-2 | Events batched (100 events or 10 seconds, whichever first) | P0 |
| FR-3 | Configurable event filter (which event types to export) | P0 |
| FR-4 | Table auto-created with correct schema if it doesn't exist | P1 |
| FR-5 | Commerce fields denormalized into top-level columns for query performance | P0 |
| FR-6 | Table partitioned by date, clustered by event_type + session_id | P0 |
| FR-7 | Failed inserts retried with exponential backoff (max 3 retries) | P0 |
| FR-8 | Export can be paused/resumed without data loss | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Event-to-BigQuery latency <30 seconds (P95) | P0 |
| NFR-2 | Data loss rate <0.1% | P0 |
| NFR-3 | Export pipeline runs server-side (not in the browser) | P0 |
| NFR-4 | Supports 10K+ events/minute without backpressure | P1 |

---

## Open Questions

1. **Server-side vs. client-side export.** Events originate client-side but BigQuery writes should happen server-side (for auth and reliability). Recommend: events are sent to a GECX backend endpoint, which handles the BigQuery streaming insert.
2. **Schema evolution.** When we add new event types, the BigQuery schema needs updating. Recommend: use JSON column for payload (flexible) + denormalized columns for common queries (performant). New event types automatically work via the JSON column.
3. **Cost management.** BigQuery streaming inserts have a cost. High-traffic deployments could generate significant data volumes. Recommend: configurable event filter to limit export scope; provide cost estimation tool.

---

## Dependencies

- **Event Bus (PRD-002):** Events flow from the bus to the export pipeline
- **Audit Trail (PRD-006):** Export data reconciled with audit trail
- **Analytics (PRD-023):** BigQuery export complements the built-in dashboard
- **BigQuery API:** Google Cloud dependency

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| BigQuery schema defined | January 2027 | Table schema and partitioning strategy |
| Streaming insert pipeline | February 2027 | Server-side batch insert working |
| Configuration UI in GECX console | March 2027 | Enable/configure export in console |
| GA | April 2027 | Available to all enterprise customers |
