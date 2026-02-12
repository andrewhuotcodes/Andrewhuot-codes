# PRD-028: Real-Time Monitoring + Anomaly Detection

**Phase:** 3 — "Make It Scale" | **Priority:** P1 | **Quarter:** Q1-Q2 2027
**Pillar:** Analytics | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

At 200+ enterprise deployments processing commerce transactions, reliability becomes critical. A spike in checkout errors, a drop in payment success rates, or an agent that suddenly stops responding needs to be detected and alerted on within minutes, not discovered hours later through customer complaints.

Real-Time Monitoring provides a live operational dashboard with anomaly detection and configurable alerting for the Chat SDK's key health metrics.

---

## What Are We Building

### Live Dashboard

A real-time operational view in the GECX console:

- **Active conversations:** Current live sessions with conversation rate
- **Message throughput:** Messages/second (sent + received)
- **Error rate:** SDK errors, API errors, timeout errors as % of interactions
- **Commerce health:** Checkout success/failure rates, payment processing latency
- **Agent response time:** P50, P95, P99 response latency
- **Widget render success:** Per-widget-type render success rate

### Anomaly Detection

Automatic detection of deviations from baseline behavior:

| Metric | Baseline | Alert Threshold |
|--------|----------|-----------------|
| Error rate | Rolling 24h average | >2x baseline for 5 minutes |
| Checkout failure rate | Rolling 24h average | >3x baseline for 5 minutes |
| Payment failure rate | Rolling 7d average | >2x baseline for 3 minutes |
| Response latency (P95) | Rolling 24h average | >3x baseline for 10 minutes |
| Session count | Rolling 24h/same-day-of-week | <50% or >200% of expected |

### Alerting

Configurable alerts via:
- Email
- PagerDuty / Opsgenie webhook
- Slack / Teams webhook
- Custom webhook (for customer's alerting system)

Alert payload:
```json
{
  "alert_id": "alert-001",
  "severity": "critical",
  "metric": "checkout_failure_rate",
  "current_value": 0.45,
  "baseline_value": 0.12,
  "deviation_factor": 3.75,
  "started_at": "2027-02-15T14:30:00Z",
  "deployment_id": "projects/kroger/...",
  "message": "Checkout failure rate is 3.75x above baseline (45% vs 12% normal)"
}
```

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Mean time to detect (MTTD) | <5 minutes for critical issues | Alert timing analysis |
| False positive rate | <10% of alerts are false positives | Alert review |
| Dashboard latency | Data within 30 seconds of real-time | Dashboard refresh timing |
| Monitoring adoption | >50% of enterprise deployments configure alerts | Configuration tracking |

### Success Criteria

1. A spike in checkout errors is detected and alerted within 5 minutes.
2. The operations team can diagnose the issue using the live dashboard without querying raw data.
3. False positive rate is below 10% (alerts are actionable, not noisy).

---

## Critical User Journeys

### CUJ 1: Payment Gateway Outage Detection
**Actor:** On-call engineer at Google GECX
**Goal:** Detect and respond to a payment gateway issue

1. A payment provider experiences an outage at 2:00 AM
2. Payment failure rate jumps from 5% to 65% across multiple merchants
3. Anomaly detection triggers within 3 minutes
4. PagerDuty alert fires: "CRITICAL: Payment failure rate 13x above baseline"
5. On-call opens live dashboard: sees which merchants are affected, which payment methods are failing
6. Identifies the affected payment gateway
7. Enables fallback payment method → failure rate drops

### CUJ 2: Merchant Monitors Their Deployment
**Actor:** Operations team at Kroger
**Goal:** Monitor their chat SDK deployment health

1. Kroger configures alerts: Slack notifications for error rate >2x baseline
2. Dashboard shows real-time metrics for their deployment
3. Tuesday afternoon: agent response latency spikes (upstream Dialogflow issue)
4. Slack alert: "WARNING: Agent response latency P95 is 8.2s (baseline 1.5s)"
5. Kroger contacts GECX support with specific data points from the dashboard

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Live dashboard with active sessions, throughput, error rate, commerce health | P0 |
| FR-2 | Data refreshes within 30 seconds of real-time | P0 |
| FR-3 | Anomaly detection on error rate, checkout failures, payment failures, latency | P0 |
| FR-4 | Configurable alert thresholds (sensitivity adjustment) | P0 |
| FR-5 | Alert channels: email, PagerDuty, Slack, custom webhook | P0 |
| FR-6 | Alert severity levels: info, warning, critical | P0 |
| FR-7 | Alert history and acknowledgment | P1 |
| FR-8 | Per-deployment and per-merchant filtering in dashboard | P1 |
| FR-9 | Incident timeline: correlate alerts with deployment changes | P2 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Dashboard supports 1000+ concurrent viewers | P0 |
| NFR-2 | Anomaly detection runs continuously (not scheduled) | P0 |
| NFR-3 | Alert delivery latency <1 minute from detection | P0 |
| NFR-4 | 90-day metric retention for trend analysis | P1 |

---

## Open Questions

1. **Should monitoring be included in all pricing tiers or enterprise-only?** Recommend: basic monitoring (dashboard) included for all; anomaly detection + alerting is enterprise tier.
2. **Integration with Google Cloud Monitoring.** Should metrics export to Cloud Monitoring for customers already using it? Recommend: yes, as a Phase 3+ enhancement.
3. **Synthetic monitoring.** Should we run synthetic test transactions to detect issues proactively? Recommend: yes for Google-managed deployments; optional for customer-managed.

---

## Dependencies

- **Event Bus (PRD-002):** All metrics derived from events
- **Analytics (PRD-023):** Monitoring shares data pipeline with analytics
- **BigQuery Export (PRD-027):** Historical trend data
- **GECX Console:** Dashboard hosted in console

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Metrics pipeline | January 2027 | Real-time aggregation from event stream |
| Live dashboard | February 2027 | Core metrics visible in GECX console |
| Anomaly detection | March 2027 | Baseline learning + deviation detection |
| Alerting integration | April 2027 | Email, PagerDuty, Slack, webhook |
| GA | May 2027 | Available to enterprise customers |
