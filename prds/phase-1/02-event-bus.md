# PRD-002: Event Bus

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Developer Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The current SDK emits four events: `loaded`, `close`, `error`, and `df-update-cart-count`. This gives developers zero visibility into what happens inside the chat — no message events, no conversation lifecycle, no commerce signals, no agent handoff notifications. Analytics, CRM integrations, custom workflows, and even basic monitoring are impossible.

The Event Bus is the nervous system of the SDK v2 architecture. Every action — sending a message, rendering a widget, updating a cart, signing a mandate, handling an agent handoff — flows through the Event Bus as a typed, timestamped, auditable event. This single system powers three critical capabilities simultaneously: developer event subscriptions, the transaction audit trail (PRD-006), and the analytics pipeline (PRD-023).

---

## What Are We Building

A typed, synchronous event bus that serves as the single source of truth for everything that happens in the SDK. Every event is an immutable object with a globally unique ID (UUIDv7), a timestamp, a typed payload, and session context.

### Event Taxonomy

The bus emits 30+ event types organized into namespaces:

| Namespace | Events | Purpose |
|-----------|--------|---------|
| `sdk:*` | `initialized`, `destroyed` | SDK lifecycle |
| `session:*` | `started`, `restored`, `ended` | Session management |
| `message:*` | `sending`, `sent`, `received`, `stream-start`, `stream-delta`, `stream-end` | Message lifecycle |
| `widget:*` | `rendered`, `interaction`, `error` | Widget lifecycle |
| `typing:*` | `user-start`, `user-stop`, `agent-start`, `agent-stop` | Typing indicators |
| `commerce:*` | `cart-updated`, `checkout-started`, `checkout-state-changed`, `escalation-started`, `escalation-completed`, `mandate-presented`, `mandate-signed`, `mandate-rejected`, `payment-started`, `payment-completed`, `payment-failed` | Commerce lifecycle |
| `agent:*` | `handoff-started`, `handoff-completed`, `human-escalation` | Agent transitions |
| `proactive:*` | `triggered`, `accepted`, `dismissed` | Proactive engagement |
| `display:*` | `opened`, `closed`, `minimized`, `maximized` | Widget display state |
| `error` | (single event) | Errors |

### Event Shape

```typescript
interface ChatEvent<T> {
  id: string;              // UUIDv7 — globally unique, time-sortable
  type: string;            // e.g., 'commerce:checkout-started'
  timestamp: number;       // Unix ms
  source: 'user' | 'agent' | 'system' | 'widget' | 'commerce';
  sessionId: string;
  conversationId: string;
  payload: T;              // typed per event
}
```

### Subscription API

```typescript
// Typed subscription — compiler enforces correct payload type
const unsub = eventBus.on('commerce:payment-completed', (event) => {
  // event.payload is typed as { orderId: string; amount: Money }
  console.log(`Order ${event.payload.orderId} completed`);
});

// Wildcard subscription — for audit logging, analytics
const unsub = eventBus.onAny((event) => {
  auditLogger.write(event);
});

// One-time subscription
eventBus.once('session:started', (event) => {
  initializeAnalytics(event.payload.sessionId);
});
```

### Architecture: Single Bus, Multiple Consumers

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ SDK Core     │    │ Commerce     │    │ Widgets      │
│              │    │ Engine       │    │              │
│  emit(...)  ─┼───►│  emit(...)  ─┼───►│  emit(...)  ─┼──┐
└──────────────┘    └──────────────┘    └──────────────┘  │
                                                           │
                    ┌──────────────────────────────────────┘
                    │  Event Bus (single instance)
                    │
          ┌─────────┼───────────┬──────────────┐
          ▼         ▼           ▼              ▼
   ┌──────────┐ ┌────────┐ ┌────────┐  ┌───────────┐
   │Developer │ │ Audit  │ │Analytics│  │ Internal  │
   │Listeners │ │ Trail  │ │Collector│  │ Consumers │
   └──────────┘ └────────┘ └────────┘  └───────────┘
```

See [CHAT_SDK_TECHNICAL_SPEC.md §3](../../CHAT_SDK_TECHNICAL_SPEC.md#3-event-bus-specification) for full type definitions.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Event subscription usage | >60% of v2 deployments subscribe to ≥1 event | SDK telemetry |
| Most-subscribed events | Identify top 10 events by subscription count | Telemetry |
| Event emission latency | P99 <2ms from trigger to all handler invocations | Performance monitoring |
| Event loss rate | 0% — no events dropped under normal operation | Integration tests |
| Audit trail coverage | 100% of commerce/session events appear in audit log | Audit verification |

### Success Criteria

1. The audit trail (PRD-006) can be implemented as a single `eventBus.onAny()` subscriber with zero changes to the event bus itself.
2. Three different integration patterns (analytics pipeline, CRM sync, custom UI) are demonstrated using only event subscriptions — no direct module coupling.
3. Event handler errors are isolated — a throwing handler does not prevent other handlers from executing or break the SDK.

---

## Critical User Journeys

### CUJ 1: Real-Time Conversion Tracking
**Actor:** Marketing team at a retailer
**Goal:** Track when chat conversations lead to purchases, in real time

```javascript
chatSDK.on('commerce:payment-completed', (event) => {
  gtag('event', 'purchase', {
    transaction_id: event.payload.orderId,
    value: event.payload.amount.amount / 100,
    currency: event.payload.amount.currency,
  });
});
```

### CUJ 2: CRM Ticket Creation on Human Escalation
**Actor:** Customer service operations team
**Goal:** Automatically create a support ticket when the agent escalates to a human

```javascript
chatSDK.on('agent:human-escalation', async (event) => {
  const history = await chatSDK.getHistory();
  await crmAPI.createTicket({
    conversationId: event.conversationId,
    transcript: history,
    queuePosition: event.payload.queuePosition,
  });
});
```

### CUJ 3: Proactive Engagement Measurement
**Actor:** Product manager optimizing engagement flows
**Goal:** Measure acceptance rate of proactive chat triggers

```javascript
const triggerCounts = {};
chatSDK.on('proactive:triggered', (event) => {
  triggerCounts[event.payload.ruleId] = (triggerCounts[event.payload.ruleId] || 0) + 1;
});
chatSDK.on('proactive:accepted', (event) => {
  analytics.track('proactive_accepted', {
    ruleId: event.payload.ruleId,
    totalTriggers: triggerCounts[event.payload.ruleId],
  });
});
```

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Event bus supports typed `on()` subscriptions that enforce payload type via ChatEventMap | P0 |
| FR-2 | Event bus supports `onAny()` wildcard subscriptions | P0 |
| FR-3 | Event bus supports `once()` single-fire subscriptions | P0 |
| FR-4 | All subscription methods return an unsubscribe function | P0 |
| FR-5 | Every event includes `id` (UUIDv7), `type`, `timestamp`, `source`, `sessionId`, `conversationId`, `payload` | P0 |
| FR-6 | All 30+ event types defined in the ChatEventMap are emitted at correct lifecycle points | P0 |
| FR-7 | Handler errors are caught, logged, and do not propagate to other handlers | P0 |
| FR-8 | Event emission is synchronous — handlers execute in registration order | P0 |
| FR-9 | Events are immutable — `Object.freeze()` applied before emission | P1 |
| FR-10 | Event bus supports namespace-based pattern subscriptions (e.g., `commerce:*`) | P2 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Event bus module is <3 KB gzipped | P0 |
| NFR-2 | P99 emission latency <2ms for ≤50 concurrent subscribers | P0 |
| NFR-3 | No memory leaks — unsubscribed handlers are garbage collected | P0 |
| NFR-4 | Bus operates correctly with 0 subscribers (no-op emission) | P0 |
| NFR-5 | UUIDv7 generation is monotonic within the same millisecond | P1 |

---

## Open Questions

1. **Should the event bus support async handlers?** Currently spec'd as synchronous. Async handlers would require the bus to handle Promises, which adds complexity and makes emission order less predictable. Recommend: keep synchronous; async work should be triggered from within handlers but not awaited by the bus.

2. **Should we support event middleware/interceptors?** Some plugin systems allow middleware that can modify or block events before they reach handlers. This is powerful but makes debugging harder. Recommend: defer to Phase 2 plugin architecture (PRD-024).

3. **How do we handle high-frequency events (like `message:stream-delta`)?** During streaming, delta events fire for every token. If a handler does expensive work on each delta, it could block rendering. Recommend: document best practices (debounce expensive handlers) and add a `requestIdleCallback` helper utility.

4. **Should events be replayable?** Storing events in a ring buffer would allow late subscribers to "catch up" on recent events. Useful for widgets that mount after the conversation starts. Recommend: implement a configurable replay buffer (last N events per type) as P2.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Event bus is exposed via `chatSDK.on()`, etc.
- **Transaction Audit Trail (PRD-006):** Primary consumer of `onAny()`
- UUIDv7 generation library (or custom implementation, ~200 bytes)

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Event taxonomy finalized | April 2026 Week 1 | All 30+ event types defined with payload shapes |
| Implementation complete | April 2026 Week 3 | Bus + UUIDv7 + error isolation working |
| Integration with audit trail | May 2026 | Audit logger consumes all events via `onAny()` |
| GA with SDK v2 | July 2026 | Shipped as part of SDK v2 Core |
