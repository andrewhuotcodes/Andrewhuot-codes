# PRD-023: Commerce Funnel Analytics

**Phase:** 2 — "Make It Intelligent" | **Priority:** P1 | **Quarter:** Q4 2026
**Pillar:** Analytics | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

Merchants deploying the Chat SDK need to measure ROI. Without conversion analytics, the SDK is a cost center with no provable revenue attribution. "Did the chat agent actually help sell more products?" is a question every VP of Commerce will ask, and we need a data-driven answer.

Commerce Funnel Analytics tracks the complete purchase journey within the chat: product views → cart additions → checkout starts → payment attempts → order confirmations. It identifies where users drop off and provides the data merchants need to optimize their agent experiences.

---

## What Are We Building

### Funnel State Machine

Every commerce interaction is tracked through a funnel:

```
Product View → Cart Add → Checkout Start → Payment → Confirmation
     │              │            │             │
     └── drop ──────┴── drop ───┴── drop ─────┘
```

### Dashboard (Merchant-Facing)

A visual analytics dashboard accessible via the GECX console:

- **Funnel visualization:** Step-by-step conversion rates with drop-off analysis
- **Time series:** Daily/weekly/monthly GMV, transaction count, average order value
- **Agent performance:** Per-agent conversion rates, response times, escalation rates
- **Widget engagement:** Which widgets drive the most interactions and conversions
- **Session replay breadcrumbs:** Event timeline for individual conversations (not video replay)

### Data Collection

Analytics data is derived from the Event Bus (PRD-002) — no additional instrumentation needed. The analytics module subscribes to commerce events and builds funnel state:

```typescript
// Analytics is just another event bus subscriber
eventBus.on('widget:interaction', trackWidgetEngagement);
eventBus.on('commerce:cart-updated', trackCartEvent);
eventBus.on('commerce:checkout-started', trackCheckoutStart);
eventBus.on('commerce:payment-completed', trackPaymentComplete);
```

### Developer API

```typescript
// Custom event tracking
chatSDK.trackEvent('product_viewed', {
  productId: 'SKU-123',
  source: 'recommendation',
});

// Analytics snapshot (for custom dashboards)
const snapshot = await chatSDK.getAnalytics();
// { sessionsToday, conversationsToday, cartAdds, checkoutStarts, completions, gmv }
```

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Analytics dashboard adoption | >60% of commerce deployments use the dashboard | Dashboard access logs |
| Data accuracy | >99% event capture rate (no dropped events) | Reconciliation with audit trail |
| Dashboard load time | <3 seconds | Performance monitoring |
| Merchant retention lift | Merchants with analytics active churn 30% less | Retention analysis |

### Success Criteria

1. A merchant can see their full commerce funnel (views → purchases) within 24 hours of deploying the SDK with commerce enabled.
2. Drop-off analysis identifies the specific checkout step where most users abandon.
3. Agent-level metrics show which agent configurations drive the best conversion rates.

---

## Critical User Journeys

### CUJ 1: Merchant Reviews Weekly Performance
**Actor:** E-commerce director at Kroger
**Goal:** Understand chat commerce ROI

1. Opens GECX console → Analytics tab
2. Sees weekly summary: 15,000 chat sessions, $127K GMV, 4.2% conversion rate
3. Funnel shows: 60% view products → 35% add to cart → 22% start checkout → 18% complete payment
4. Identifies checkout drop-off: 22% → 18% (payment step loses 18% of users)
5. Drills into payment step: users are dropping when asked for card info (Google Pay adoption is 45%)
6. Action: enable Google Pay as the default to reduce friction

### CUJ 2: Developer Tracks Custom Events
**Actor:** Developer building a custom product recommendation widget
**Goal:** Measure widget effectiveness

1. Developer adds `chatSDK.trackEvent('recommendation_shown', { count: 4 })` when their widget renders
2. Adds `chatSDK.trackEvent('recommendation_clicked', { productId })` on product click
3. Dashboard shows recommendation CTR: 32% click rate, 8% conversion to purchase
4. Developer iterates on widget design using the data

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Funnel tracking from product view through order confirmation | P0 |
| FR-2 | Dashboard with funnel visualization and drop-off analysis | P0 |
| FR-3 | Time series charts (daily/weekly/monthly) for GMV and transactions | P0 |
| FR-4 | Per-agent performance metrics (conversion rate, response time) | P1 |
| FR-5 | Widget engagement metrics (interactions per widget type) | P1 |
| FR-6 | `trackEvent()` API for custom developer events | P0 |
| FR-7 | `getAnalytics()` API for programmatic access | P1 |
| FR-8 | Data derived from Event Bus subscriptions (no additional instrumentation) | P0 |
| FR-9 | Real-time data (analytics update within 5 minutes of events) | P1 |
| FR-10 | Export to CSV/PDF from dashboard | P2 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Analytics collector module is <4 KB gzipped, lazy loaded | P0 |
| NFR-2 | Event batching: events sent in batches every 10 seconds (not per-event) | P0 |
| NFR-3 | Dashboard loads in <3 seconds | P0 |
| NFR-4 | 90-day data retention (configurable) | P1 |

---

## Open Questions

1. **Should analytics data go to the customer's own analytics system (GA4, Mixpanel)?** Recommend: yes, via event bus subscribers. The customer can subscribe to events and forward them to any analytics system. The GECX dashboard is the default but not the only option.

2. **Privacy compliance.** Analytics must not track PII. Recommend: user IDs are pseudonymized (SHA-256); analytics are aggregated; individual session data is accessible only via the audit trail (PRD-006).

---

## Dependencies

- **Event Bus (PRD-002):** Analytics subscribes to commerce/widget events
- **Audit Trail (PRD-006):** Session replay breadcrumbs leverage audit data
- **GECX Console:** Dashboard hosted in the existing console UI

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Event collection pipeline | October 2026 | Commerce events aggregated and stored |
| Funnel dashboard | November 2026 | Visualization with drop-off analysis |
| Agent + widget metrics | November 2026 Week 3 | Per-agent and per-widget breakdowns |
| GA | December 2026 | Shipped with Phase 2 |
