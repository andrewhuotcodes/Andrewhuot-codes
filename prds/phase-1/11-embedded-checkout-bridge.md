# PRD-011: Embedded Checkout Bridge

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q3 2026
**Pillar:** Protocol Commerce | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

UCP's three-state checkout model includes a `requires_escalation` state. This state means the agent cannot complete the checkout autonomously — the merchant requires human input that goes beyond what the agent can handle. Examples: complex shipping configurations, age verification, custom product personalization, regulatory disclosures, or payment methods the agent doesn't support.

When `requires_escalation` fires, UCP returns a `continueUrl` pointing to the merchant's own checkout experience. The SDK must render this merchant experience inside the chat thread — seamlessly, securely, and without breaking the conversation flow. When the merchant signals completion, the SDK closes the embedded checkout and returns the user to the conversation.

This is architecturally a browser-within-a-browser: the merchant gets full control of their checkout UX, the SDK gets the completion signal, and the user stays in the thread.

---

## What Are We Building

A sandboxed iframe bridge that loads the merchant's checkout page inside the chat widget, communicates via JSON-RPC 2.0 over `postMessage`, and returns the user to the conversation on completion.

### Flow

```
Agent initiates checkout
        │
        ▼
UCP returns: { status: 'requires_escalation', continueUrl: 'https://merchant.com/checkout/abc' }
        │
        ▼
SDK displays: "Completing checkout with Merchant..."
        │
        ▼
┌──────────────────────────────────┐
│ Merchant Checkout (sandboxed     │
│ iframe)                          │
│                                  │
│  Merchant's full checkout        │
│  experience loads here:          │
│  - Shipping config               │
│  - Age verification              │
│  - Custom options                │
│  - Payment                       │
│                                  │
│  ┌─────────────────────────────┐ │
│  │ JSON-RPC 2.0 communication  │ │
│  │ ← checkout.init             │ │
│  │ → checkout.progress         │ │
│  │ → checkout.resize           │ │
│  │ → checkout.complete         │ │
│  └─────────────────────────────┘ │
└──────────────────────────────────┘
        │
        ▼ (merchant signals completion)
Iframe closes, conversation resumes
        │
        ▼
Agent: "Your order is confirmed! Order #12345"
```

### JSON-RPC 2.0 Protocol

Communication between the SDK (parent) and merchant iframe (child):

**SDK → Merchant:**
- `checkout.init` — sends session context (session ID, locale, theme tokens)
- `checkout.cancel` — user or SDK cancels the checkout

**Merchant → SDK:**
- `checkout.progress` — reports progress (step name, optional data)
- `checkout.resize` — requests iframe height change
- `checkout.complete` — checkout finished (order ID, status)

### Security Model

The merchant iframe is sandboxed:
```html
<iframe
  src="https://merchant.com/checkout/abc"
  sandbox="allow-scripts allow-forms allow-popups allow-same-origin"
  allow="payment"
  referrerpolicy="strict-origin"
></iframe>
```

- **Origin validation:** SDK only accepts messages from the expected merchant origin
- **No top-level navigation:** Merchant cannot navigate the host page (`allow-top-navigation` excluded)
- **Timeout:** If the merchant page doesn't send `checkout.complete` or `checkout.progress` within a configurable timeout (default: 15 minutes), the SDK shows a timeout message and offers to cancel

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Escalation completion rate | >70% of escalated checkouts complete successfully | Commerce funnel |
| Escalation-to-completion time | <5 minutes (median) | Timestamp analysis |
| Timeout rate | <10% of escalated checkouts time out | Timeout tracking |
| JSON-RPC handshake success | >99% of iframes successfully complete `checkout.init` | Protocol monitoring |

### Success Criteria

1. A user enters the embedded checkout, completes the merchant's flow, and seamlessly returns to the chat conversation with an order confirmation.
2. If the user cancels mid-flow or the merchant page errors, the user returns to the chat with a clear message and the ability to retry or ask for help.
3. The merchant iframe cannot access the host page's DOM, cookies, or localStorage.

---

## Critical User Journeys

### CUJ 1: Successful Embedded Checkout
**Actor:** User purchasing a customizable product
**Goal:** Complete a checkout that requires merchant-specific configuration

1. User builds a custom kitchen setup through the chat agent
2. Agent initiates checkout → UCP returns `requires_escalation` (merchant needs specific configuration confirmation)
3. SDK shows transition: "Opening secure checkout with KitchenBrand..."
4. Merchant checkout page loads in the iframe with the pre-filled order
5. User confirms custom color selection and delivery scheduling
6. User completes payment on merchant's page
7. Merchant sends `checkout.complete({ orderId: 'KB-789' })`
8. Iframe fades out, conversation resumes
9. Agent: "Your custom kitchen order #KB-789 is confirmed! Estimated delivery: March 15."

### CUJ 2: User Cancels Embedded Checkout
**Actor:** User who decides not to complete the merchant checkout
**Goal:** Return to the conversation without completing the purchase

1. Merchant checkout loads in iframe
2. User decides the shipping options don't work for them
3. User taps "Back to chat" button (rendered by SDK above the iframe)
4. SDK sends `checkout.cancel({ reason: 'user_cancelled' })` to merchant
5. Iframe closes, conversation resumes
6. Agent: "No problem! Would you like me to look for alternative products with better shipping options?"

### CUJ 3: Merchant Page Timeout
**Actor:** User on a slow connection
**Goal:** Handle the case where the merchant page fails to load or respond

1. `requires_escalation` triggers, SDK opens iframe
2. Merchant page takes too long to load (network issue)
3. After 30 seconds without `checkout.init` response, SDK shows: "The merchant's checkout is taking longer than expected."
4. After 15 minutes without progress, SDK shows: "The checkout session has timed out."
5. User is offered: [Try Again] [Cancel and Ask for Help]

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | SDK detects `requires_escalation` state from UCP checkout and opens embedded checkout | P0 |
| FR-2 | Merchant's `continueUrl` loads in a sandboxed iframe within the chat widget | P0 |
| FR-3 | SDK sends `checkout.init` with session context (session ID, locale, theme) via JSON-RPC 2.0 | P0 |
| FR-4 | SDK receives `checkout.progress` messages and optionally displays progress to user | P1 |
| FR-5 | SDK receives `checkout.resize` and adjusts iframe height accordingly | P0 |
| FR-6 | SDK receives `checkout.complete` and closes iframe, resuming conversation | P0 |
| FR-7 | "Back to chat" / cancel button is always visible above the iframe | P0 |
| FR-8 | Cancel sends `checkout.cancel` to merchant before closing iframe | P0 |
| FR-9 | Timeout handling: configurable timeout (default 15 min) with user notification | P0 |
| FR-10 | Origin validation on all `postMessage` communication | P0 |
| FR-11 | Escalation events are captured by Audit Trail (PRD-006) | P0 |
| FR-12 | Loading state animation shown while merchant page loads | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Iframe `sandbox` attribute excludes `allow-top-navigation` | P0 |
| NFR-2 | Merchant page cannot access host page DOM, cookies, or storage | P0 |
| NFR-3 | Bridge module is <5 KB gzipped (part of commerce module) | P0 |
| NFR-4 | Iframe loads with `loading="lazy"` to not block initial page render | P1 |

---

## Open Questions

1. **What if the merchant doesn't implement JSON-RPC 2.0?** Not all merchants will adopt the messaging protocol immediately. Recommend: fall back to polling the UCP checkout session status endpoint. When the session transitions from `requires_escalation` to another state, close the iframe.

2. **Can the merchant theme the iframe to match the chat?** Theme tokens are sent via `checkout.init`, but the merchant controls their own CSS. Recommend: provide theme tokens as a suggestion; the merchant decides whether to use them.

3. **Mobile experience — iframe scrolling.** Nested scrolling (chat scrolls and iframe scrolls) is a UX anti-pattern on mobile. Recommend: on mobile, embedded checkout goes full-screen (replaces the chat UI entirely) with a persistent header bar for cancel/back.

4. **Google Pay within the embedded checkout.** If the merchant's checkout page triggers Google Pay, it needs `allow-popups` and `allow-scripts`. This is already in the sandbox attributes but needs testing across browsers.

---

## Dependencies

- **Commerce Engine (PRD-009):** Detects `requires_escalation` state
- **Event Bus (PRD-002):** Escalation events
- **Audit Trail (PRD-006):** Escalation events audited
- **Mobile Design (PRD-008):** Full-screen mobile behavior
- **Iframe Sandbox (PRD-007):** Shared iframe security patterns

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| JSON-RPC protocol spec published | June 2026 Week 2 | Protocol doc shared with merchant partners |
| Iframe bridge implementation | July 2026 | Open, communicate, close cycle working |
| Merchant testing (1 partner) | August 2026 | End-to-end with at least one merchant |
| Mobile full-screen mode | August 2026 Week 3 | Full-screen checkout on mobile |
| GA | September 2026 | Shipped with Phase 1 Commerce |
