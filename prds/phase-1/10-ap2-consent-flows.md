# PRD-010: AP2 Consent Flows

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q3 2026
**Pillar:** Trust | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Agent Payments Protocol (AP2) is Google's framework for securing agentic transactions. At its core, AP2 introduces **Mandates** — cryptographically signed consent artifacts that prove the user explicitly authorized a specific action. There are three mandate types, forming a chain of consent:

1. **Intent Mandate:** User authorizes the agent to shop on their behalf (scope, budget)
2. **Checkout Mandate:** User agrees to specific items, prices, and merchant terms
3. **Payment Mandate:** User authorizes a specific payment amount via a specific method

Without visible, signable mandates in the chat thread, UCP checkout is either unauthorized (regulatory risk) or requires external redirect flows that break the conversation. AP2 mandates rendered inline are the bridge between "agent found you a product" and "you authorized this purchase."

---

## What Are We Building

A mandate rendering and signing system that presents AP2 mandates as clear, interactive consent cards within the chat thread. Users can review exactly what they're authorizing, sign (accept), reject, or request modifications — all within the conversation flow.

### Mandate Card Widget

Each mandate type renders as a distinct card with specific content:

**Intent Mandate Card:**
```
┌─────────────────────────────────────────┐
│ 🔒 Authorization Request                │
│                                          │
│ Shopping Assistant wants to:             │
│ • Search for products matching your      │
│   preferences                            │
│ • Compare prices across merchants        │
│ • Add items to your cart                 │
│                                          │
│ Budget limit: $200.00                    │
│ Expires: 30 minutes                      │
│                                          │
│ [Authorize]              [Decline]       │
└─────────────────────────────────────────┘
```

**Checkout Mandate Card:**
```
┌─────────────────────────────────────────┐
│ 🔒 Purchase Authorization               │
│                                          │
│ Merchant: Kroger                         │
│                                          │
│ Items:                                   │
│  1x Ninja Professional Blender   $79.99 │
│  2x Kitchen Towels (Set of 4)     $9.98 │
│                                          │
│ Subtotal:        $89.97                  │
│ Store Pickup:     FREE                   │
│ Tax:              $7.20                  │
│ ─────────────────────────                │
│ Total:           $97.17                  │
│                                          │
│ By authorizing, you agree to Kroger's    │
│ terms of sale.                           │
│                                          │
│ [Authorize Purchase]     [Decline]       │
│                                          │
│ ⏱ Expires in 14:32                      │
└─────────────────────────────────────────┘
```

**Payment Mandate Card:**
```
┌─────────────────────────────────────────┐
│ 🔒 Payment Authorization                │
│                                          │
│ Pay $97.17 to Kroger                     │
│                                          │
│ Payment method:                          │
│ Google Pay •••• 4242                     │
│                                          │
│ This authorizes a one-time charge of     │
│ $97.17 USD to your Visa ending in 4242.  │
│                                          │
│ [Pay $97.17]              [Cancel]       │
│                                          │
│ ⏱ Expires in 4:58                       │
└─────────────────────────────────────────┘
```

### Signing Flow

1. Agent presents mandate → SDK renders the mandate card
2. User reviews the details
3. User taps "Authorize" / "Pay" → SDK generates a cryptographic signature
4. Signature is sent back to the agent with the mandate ID
5. Agent includes the signed mandate in the UCP checkout/payment request
6. Merchant verifies the signature chain (intent → checkout → payment)

### Mandate Lifecycle Events

```
commerce:mandate-presented  →  User sees the mandate card
commerce:mandate-signed     →  User approved and signed
commerce:mandate-rejected   →  User declined
```

All mandate events are captured by the Transaction Audit Trail (PRD-006) with complete mandate data — providing cryptographic proof of what the user consented to.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Mandate sign rate (Intent) | >80% of presented mandates signed | Mandate analytics |
| Mandate sign rate (Checkout) | >70% of presented mandates signed | Mandate analytics |
| Mandate sign rate (Payment) | >90% of presented mandates signed | Mandate analytics |
| Average time to sign (all types) | <15 seconds | Timestamp analysis |
| Mandate expiration rate | <5% expire before user action | Mandate analytics |
| Audit trail coverage | 100% of mandates have corresponding audit records | Reconciliation |

### Success Criteria

1. A user who has never seen a mandate card understands what they're authorizing within 5 seconds of viewing (verified by usability testing).
2. The mandate chain (intent → checkout → payment) is cryptographically verifiable by the merchant.
3. Every mandate presentation, signing, and rejection is captured in the audit trail with the complete mandate content.
4. Expired mandates are clearly indicated and cannot be signed after expiration.

---

## Critical User Journeys

### CUJ 1: Standard Purchase Flow with Mandates
**Actor:** Consumer purchasing through a shopping agent
**Goal:** Complete a purchase with proper authorization at each step

1. User: "Find me a blender under $100"
2. Agent presents Intent Mandate: "I'd like to search and compare blenders for you. Budget: $100."
3. User reviews scope → taps "Authorize" → intent signed
4. Agent searches, presents options, user selects one
5. Agent presents Checkout Mandate: specific item, price, merchant, total
6. User reviews line items and total → taps "Authorize Purchase" → checkout signed
7. Agent presents Payment Mandate: exact amount, payment method
8. User confirms → taps "Pay $79.99" → payment signed
9. Payment processes → order confirmed

### CUJ 2: User Declines a Mandate
**Actor:** Consumer who changes their mind
**Goal:** Decline a checkout mandate and modify the order

1. Agent presents Checkout Mandate with 3 items totaling $247
2. User thinks $247 is too much → taps "Decline"
3. Agent receives `mandate-rejected` event
4. Agent: "No problem. Would you like to remove any items?"
5. User: "Remove the third item"
6. Agent presents a new Checkout Mandate with 2 items totaling $168
7. User taps "Authorize Purchase"

### CUJ 3: Mandate Expires
**Actor:** Distracted consumer
**Goal:** Handle an expired mandate gracefully

1. Agent presents Payment Mandate (15-minute expiry)
2. User gets distracted, doesn't respond for 15 minutes
3. Countdown reaches zero → mandate card updates to show "Expired"
4. "Authorize" button is disabled, replaced with "Request New Authorization"
5. User taps "Request New Authorization"
6. Agent generates a new mandate with fresh pricing (prices may have changed)

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Mandate card widget renders Intent, Checkout, and Payment mandates with distinct layouts | P0 |
| FR-2 | Checkout mandate shows complete line items, prices, totals, and merchant identity | P0 |
| FR-3 | Payment mandate shows exact amount, currency, and payment method | P0 |
| FR-4 | "Authorize" / "Pay" button triggers cryptographic signing of the mandate | P0 |
| FR-5 | "Decline" button emits `commerce:mandate-rejected` event | P0 |
| FR-6 | Signed mandates emit `commerce:mandate-signed` with signature | P0 |
| FR-7 | Mandate cards show a live countdown timer for expiration | P1 |
| FR-8 | Expired mandates are visually indicated and buttons are disabled | P0 |
| FR-9 | Mandate content is frozen after presentation — cannot be modified by the agent | P0 |
| FR-10 | All mandate events are captured by the Audit Trail (PRD-006) | P0 |
| FR-11 | Merchant logo/name displayed on checkout and payment mandates | P1 |
| FR-12 | Mandate cards link to merchant terms of sale (if provided by UCP) | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Mandate card renders in <200ms | P0 |
| NFR-2 | Cryptographic signing completes in <500ms using Web Crypto API | P0 |
| NFR-3 | Mandate content is not modifiable via DOM manipulation (integrity protection) | P0 |
| NFR-4 | Mandate cards are fully keyboard-navigable and screen reader accessible | P0 |
| NFR-5 | Mandate cards render correctly on mobile (single-column layout) | P0 |

---

## Open Questions

1. **What cryptographic algorithm for signing?** AP2 spec suggests ECDSA with P-256. Need to confirm this is supported in Web Crypto API across all target browsers. Recommend: ECDSA P-256 with SHA-256.

2. **Where is the signing key stored?** The user's private key for mandate signing needs to be securely generated and stored. Options: (a) generated per session (no persistence), (b) stored in credential manager, (c) backed by Google Pay cryptographic identity. Recommend: align with AP2's key management spec; likely per-session keys initially.

3. **Should users be able to modify mandates?** Currently, mandates are take-it-or-leave-it. Could we allow users to adjust quantities or remove items from a checkout mandate without rejecting it entirely? Recommend: reject + re-present flow in Phase 1; inline modification as Phase 2 enhancement.

4. **How do we handle multiple currencies?** A cross-merchant checkout might involve merchants in different currencies. Recommend: mandates always show the amount in the merchant's currency; the SDK shows a conversion estimate if different from the user's locale currency.

---

## Dependencies

- **Widget Registry (PRD-003):** Mandate cards are registered widgets
- **Commerce Engine (PRD-009):** Mandates are presented during checkout
- **Audit Trail (PRD-006):** All mandate events are audited
- **Accessibility (PRD-005):** Mandate cards must be screen-reader accessible
- **AP2 backend:** Mandate generation and verification endpoints

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Mandate card designs finalized | June 2026 Week 2 | UX design for all 3 mandate types |
| Intent + Checkout mandate rendering | July 2026 | Cards render with full content |
| Cryptographic signing | August 2026 | ECDSA signing via Web Crypto API |
| Payment mandate + expiry | August 2026 Week 3 | Full lifecycle including expiration |
| Audit integration verified | September 2026 | All mandates in audit trail |
| GA | September 2026 | Shipped with Phase 1 Commerce |
