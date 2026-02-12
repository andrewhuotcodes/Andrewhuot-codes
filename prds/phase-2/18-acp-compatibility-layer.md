# PRD-018: ACP Compatibility Layer

**Phase:** 2 — "Make It Intelligent" | **Priority:** P0 | **Quarter:** Q4 2026
**Pillar:** Protocol Commerce | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

OpenAI launched the Agentic Commerce Protocol (ACP) in partnership with Stripe in September 2025. ACP enables ChatGPT and other agents to complete purchases via Stripe-powered checkout. With 50M purchase-intent interactions daily on ChatGPT and Stripe's dominance in online payments, ACP is rapidly becoming the alternative commerce protocol to Google's UCP.

Strategic reality: merchants will implement multiple protocols. A merchant already on Stripe (millions of them) will adopt ACP with minimal effort. That same merchant may also join the UCP coalition for Google Shopping distribution. The Chat SDK must render both — making the SDK protocol-agnostic at the UI layer.

This isn't about picking a winner. It's about ensuring the Chat SDK can render commerce flows regardless of which protocol powers the backend, so merchants aren't forced to choose.

---

## What Are We Building

A compatibility layer that translates ACP checkout sessions into the SDK's widget system, rendering Stripe-powered checkout flows alongside UCP flows in the same thread.

### Architecture

```
Agent request: "Checkout with ACP merchant"
        │
        ▼
Commerce Engine
├── UCP Adapter (existing) ──► UCP API ──► UCP Merchant
└── ACP Adapter (new)      ──► ACP API ──► Stripe/ACP Merchant
        │
        ▼ (both adapters produce the same internal types)
SDK Widget System (protocol-agnostic)
        │
        ▼
Cart Widget / Checkout Flow / Payment / Confirmation
(same widgets, same UX — user doesn't know which protocol)
```

### Protocol Translation

ACP concepts map to SDK internal types:

| ACP Concept | SDK Internal Type | Notes |
|-------------|-------------------|-------|
| ACP Cart | `CartState` with `MerchantCart` | Line items, quantities, prices |
| ACP Checkout Session | `CheckoutSession` | Mapped to SDK's state machine |
| Stripe Payment Intent | `PaymentMethod` selection | Stripe Elements or Google Pay |
| ACP Order Confirmation | `OrderConfirmation` | Order ID, items, totals |

### Payment Handling

ACP checkouts use Stripe for payment. Two paths:
1. **Google Pay via Stripe:** Stripe's payment sheet can accept Google Pay tokens — user taps Google Pay, gets the same one-tap experience
2. **Stripe Elements:** For card entry, Stripe Elements renders inside a sandboxed container within the checkout widget

### User Experience

From the user's perspective, UCP and ACP checkouts look identical. Same cart widget, same checkout flow, same payment step, same confirmation. The protocol difference is invisible. The only visible difference might be the merchant's branding.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| ACP checkout completion rate | Within 10% of UCP completion rate | Commerce funnel comparison |
| ACP merchants rendered | 10+ merchants live | Deployment tracking |
| Dual-protocol deployments | 5+ merchants using both UCP and ACP | Configuration tracking |
| Protocol detection accuracy | >99% correct routing | Protocol analytics |

### Success Criteria

1. A user can check out with a UCP merchant and an ACP merchant in the same conversation, with identical UX for both.
2. A merchant already using Stripe/ACP can be rendered in the Chat SDK with <1 week of integration effort.
3. The compatibility layer adds <8 KB gzipped to the commerce module (lazy loaded).

---

## Critical User Journeys

### CUJ 1: Cross-Protocol Comparison Shopping
**Actor:** User comparing products from UCP and ACP merchants
**Goal:** Buy from the best option regardless of which protocol the merchant uses

1. User: "Find me a leather wallet under $100"
2. Agent shows products from Merchant A (UCP) and Merchant B (ACP/Stripe)
3. User picks a wallet from Merchant B (ACP)
4. Checkout flow renders with the same widgets used for UCP
5. Payment step: Google Pay button (Stripe accepts Google Pay tokens)
6. User taps Google Pay → payment processes via Stripe
7. Order confirmation renders in the same format as UCP orders
8. User has no idea which protocol was used

### CUJ 2: Merchant with Both Protocols
**Actor:** Merchant who has both UCP and Stripe/ACP
**Goal:** SDK uses the optimal checkout path

1. Agent initiates checkout for a merchant available on both UCP and ACP
2. Commerce engine selects the preferred protocol (configurable; default: UCP)
3. If UCP checkout fails or enters `requires_escalation`, falls back to ACP
4. User experiences seamless checkout regardless of backend routing

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | ACP adapter translates ACP cart/checkout to SDK internal types | P0 |
| FR-2 | Cart widget renders ACP items identically to UCP items | P0 |
| FR-3 | Checkout flow widget handles ACP checkout state transitions | P0 |
| FR-4 | Google Pay works with Stripe's payment sheet for ACP checkouts | P0 |
| FR-5 | Stripe Elements can render for card entry in ACP checkouts | P0 |
| FR-6 | Commerce events are emitted identically for ACP and UCP (protocol field in metadata) | P0 |
| FR-7 | Audit trail captures ACP transactions with the same completeness as UCP | P0 |
| FR-8 | Protocol preference is configurable per deployment (`preferredProtocol: 'ucp' | 'acp'`) | P1 |
| FR-9 | Fallback: if preferred protocol checkout fails, try alternative protocol | P2 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | ACP adapter is <8 KB gzipped, lazy loaded on first ACP interaction | P0 |
| NFR-2 | ACP checkout latency within 200ms of equivalent UCP checkout | P0 |
| NFR-3 | Stripe.js is loaded lazily only when ACP payment is needed | P0 |

---

## Open Questions

1. **Stripe.js loading.** Stripe requires their JS library for payment processing. This is an external dependency (~25 KB). Should we always load it or only when ACP is detected? Recommend: lazy load only when an ACP checkout reaches the payment step.

2. **ACP protocol versioning.** ACP is new and evolving. How do we handle breaking changes? Recommend: version the adapter and maintain backward compatibility for at least 2 ACP versions.

3. **Who configures ACP merchant credentials?** Stripe API keys are needed for payment processing. Recommend: configured in the GECX backend, not in the client-side SDK.

4. **Should we support Klarna's APP as well?** Klarna's Agentic Product Protocol covers product discovery. Recommend: evaluate in Phase 3 based on APP adoption.

---

## Dependencies

- **Commerce Engine (PRD-009):** ACP adapter plugs into the commerce engine
- **Google Pay (PRD-012):** Google Pay works with Stripe
- **Audit Trail (PRD-006):** ACP transactions audited
- **Stripe/ACP API:** External dependency

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| ACP protocol analysis | September 2026 | Full API mapping UCP ↔ ACP |
| ACP adapter implementation | October 2026 | Cart + checkout translation working |
| Stripe payment integration | November 2026 | Google Pay + card entry via Stripe |
| Dual-protocol testing | November 2026 Week 3 | UCP + ACP in same conversation |
| GA | December 2026 | Shipped with Phase 2 |
