# PRD-020: Proactive Engagement Engine

**Phase:** 2 — "Make It Intelligent" | **Priority:** P1 | **Quarter:** Q4 2026
**Pillar:** Proactive | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Chat SDK is entirely reactive — it waits for the user to click the chat bubble. It has no ability to initiate contact based on user behavior, page context, or business rules. Meanwhile, the average e-commerce site has a 70% cart abandonment rate, users spend 30+ seconds on product pages without engaging, and error states go unassisted.

The Proactive Engagement Engine shifts the SDK from passive to anticipatory. It monitors user behavior signals (time on page, scroll depth, cart state, error encounters) and triggers contextual, non-intrusive engagement. The difference between "proactive" and "annoying" is context and timing — the engine provides both.

---

## What Are We Building

### Signal Detection

The engine monitors configurable behavioral signals:

| Signal | Example | Default Threshold |
|--------|---------|-------------------|
| Time on page | User on product page >30s without action | 30 seconds |
| Cart abandonment | Cart has items, user navigates away | Navigation event with items in cart |
| Scroll depth | User scrolls to bottom of product specs | >80% scroll depth |
| Error encounter | User hits a 404, form validation error | Error event on page |
| Repeated search | User searches the same term 3+ times | 3 searches for similar terms |
| Checkout hesitation | User on payment step for >60s | 60 seconds on step |
| Return visit | User returns to a product viewed >24h ago | Page view matching history |

### Trigger Rules

Developers configure triggers via the Smart Triggers API:

```typescript
chatSDK.registerTrigger({
  id: 'product_page_help',
  signals: [
    { type: 'time_on_page', threshold: 30000, page: '/products/*' },
    { type: 'scroll_depth', threshold: 0.8 },
  ],
  operator: 'AND',           // all signals must fire
  cooldown: 3600000,          // don't re-trigger for 1 hour
  maxPerSession: 1,           // maximum 1 trigger per session
  message: {
    text: 'Need help choosing? I can compare sizes and features.',
    action: { label: 'Get Help', payload: { intent: 'product_help' } },
  },
});
```

### Engagement UI

Proactive engagement renders as a non-intrusive notification:

```
                                    ┌──────────────────────────┐
                                    │ 💡 Need help choosing?   │
                                    │ I can compare sizes      │
                                    │ and features.            │
                                    │                          │
                                    │ [Get Help]  [Dismiss]    │
                                    └──────────────────────────┘
                                              ╱
                                    ┌────────┐
                                    │  💬    │  ← chat bubble
                                    └────────┘
```

- Non-modal — does not block interaction with the page
- Dismissible — user can close it permanently (respects the cooldown/max settings)
- Contextual — message content relates to the user's current behavior
- Accessible — screen reader announces the notification via `aria-live`

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Engagement rate (trigger → user opens chat) | >12% | Event tracking |
| Conversion lift (proactive vs. passive users) | >15% purchase rate lift | A/B testing |
| Dismissal rate | <50% (indicates triggers are contextually relevant) | Event tracking |
| Cart recovery rate (abandonment triggers) | >8% of abandoned carts recovered | Commerce analytics |
| User annoyance (reported via feedback) | <2% of triggered users report annoyance | Feedback mechanism |

### Success Criteria

1. Cart abandonment triggers recover >8% of abandoned carts.
2. Product page engagement triggers increase chat opens by >20% vs. passive bubble.
3. Users who engage with proactive triggers have >15% higher purchase rates.
4. <2% of users report the proactive engagement as annoying.

---

## Critical User Journeys

### CUJ 1: Cart Abandonment Recovery
**Actor:** User who is about to leave with items in cart
**Goal:** Recover an abandoned cart

1. User has a $200 blender in their cart
2. User moves mouse toward browser tab/address bar (exit intent on desktop) or taps back button (mobile)
3. Trigger fires: notification badge appears on chat bubble
4. Message: "You have a $200 blender in your cart. Want me to check if there's a coupon?"
5. User taps "Check for Coupons"
6. Agent finds a 10% off code → user saves $20 → completes purchase

### CUJ 2: Product Page Assistance
**Actor:** User who seems stuck on a product page
**Goal:** Offer contextual help

1. User has been on a laptop product page for 45 seconds, scrolled through specs
2. Trigger fires (time + scroll depth): "Need help deciding? I can compare this with similar laptops."
3. User taps "Get Help"
4. Chat opens with product context already set
5. Agent: "I see you're looking at the Dell XPS 15. Want me to compare it with the MacBook Pro and ThinkPad X1?"

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | `registerTrigger()` accepts trigger rules with signals, operator, cooldown, and message | P0 |
| FR-2 | Signal types: time_on_page, scroll_depth, cart_state, error, navigation, custom | P0 |
| FR-3 | Trigger operators: AND (all signals), OR (any signal) | P0 |
| FR-4 | Cooldown prevents re-triggering within configured period | P0 |
| FR-5 | `maxPerSession` limits total triggers per session | P0 |
| FR-6 | Engagement renders as non-modal notification near the chat bubble | P0 |
| FR-7 | "Dismiss" removes the notification and respects cooldown | P0 |
| FR-8 | `proactive:triggered`, `proactive:accepted`, `proactive:dismissed` events emitted | P0 |
| FR-9 | Exit-intent detection for desktop (mouse movement) and mobile (visibility change) | P1 |
| FR-10 | Custom signal API: developers can fire custom signals programmatically | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Signal monitoring adds <1% CPU overhead to the page | P0 |
| NFR-2 | Proactive module is lazy-loaded (~5 KB gzipped) | P0 |
| NFR-3 | Notification is accessible (aria-live announcement, keyboard dismissible) | P0 |
| NFR-4 | Notification respects `prefers-reduced-motion` (no slide animation) | P1 |

---

## Open Questions

1. **ML-driven triggers vs. rule-based triggers.** Should Phase 2 include ML-powered trigger optimization? Recommend: rule-based in Phase 2; ML optimization (learning which triggers work best) in Phase 3.

2. **Global opt-out.** Should users be able to permanently disable proactive engagement? Recommend: yes, via a setting in the chat menu. Stored in user preferences.

3. **A/B testing of triggers.** Developers need to test different trigger messages and thresholds. Recommend: use the A/B testing framework (deferred feature) or integrate with existing A/B testing tools via the event bus.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Trigger registration API
- **Event Bus (PRD-002):** Proactive events
- **Commerce Engine (PRD-009):** Cart state signals
- **Mobile Design (PRD-008):** Mobile notification rendering

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Signal detection framework | October 2026 | Time, scroll, cart, error signals working |
| Trigger rule engine | October 2026 Week 3 | Rule evaluation with AND/OR, cooldown |
| Notification UI | November 2026 | Non-modal, dismissible, accessible |
| Cart abandonment trigger | November 2026 Week 2 | First production trigger |
| GA | December 2026 | Shipped with Phase 2 |
