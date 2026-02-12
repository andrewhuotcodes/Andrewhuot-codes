# PRD-009: UCP-Native Inline Checkout

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q3 2026
**Pillar:** Protocol Commerce | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Unified Commerce Protocol (UCP) defines the full commerce lifecycle — product discovery, cart management, checkout, payment, and fulfillment — as an open standard. Google co-authored UCP with Shopify and 20+ brand partners. It launched at NRF 2026 (January 11, 2026) under Apache 2.0.

But a protocol without a front-end is a specification without a product. Today, UCP exists as backend API documentation. No user has ever completed a UCP checkout inside a chat thread. The SDK has a cart-count event and an Order Summary widget, but no actual commerce primitives — no cart management, no checkout flow, no payment selection, no fulfillment options.

This feature makes UCP real for end users by implementing the complete checkout lifecycle as first-class conversation elements rendered inline within the chat thread.

---

## What Are We Building

A complete commerce engine that implements UCP's three-state checkout model (`incomplete` → `requires_escalation` → `ready_for_complete`) as interactive widgets within the chat thread.

### The Commerce State Machine

```
              addToCart()
  [idle] ─────────────► [cart_open]
                              │
                    initiateCheckout()
                              │
                              ▼
                        [checkout_initiated]
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
              [incomplete]    [requires_escalation]
              (missing info)  (merchant checkout needed)
                     │                 │
              fill missing      embedded checkout
                     │           (PRD-011)
                     ▼                 │
              [ready_for_complete]◄────┘
                     │
              completeCheckout()
                     │
                     ▼
              [processing_payment]
                     │
              ┌──────┴──────┐
              ▼              ▼
         [completed]    [error]
```

### Inline Widgets

**Cart Widget:** Shows current cart contents with per-item quantity controls, remove buttons, and running total. Supports cross-merchant carts (Phase 2) with per-merchant subtotals. Updates in real time as the agent adds or modifies items.

**Checkout Flow Widget:** Multi-step inline checkout rendered as a compact, scrollable form within the chat bubble:
- **Step 1 — Review:** Line items, totals, applied discounts
- **Step 2 — Fulfillment:** Shipping/pickup/delivery options (from UCP fulfillment extensions)
- **Step 3 — Payment:** Payment method selection (Google Pay default, cards, etc.)
- **Step 4 — Confirm:** Final summary with "Place Order" button

**Payment Method Selector:** Lists available payment handlers from UCP capability negotiation. Google Pay is the default, rendered as the primary action. Additional methods (cards, PayPal, etc.) are shown as secondary options.

**Order Confirmation Widget:** After successful payment, shows order ID, line items, estimated delivery, and tracking link within the thread.

### Commerce API

```typescript
// Available via chatSDK.getCommerce()
interface CommerceEngine {
  getCart(): CartState;
  addToCart(merchantId: string, item: LineItem): void;
  removeFromCart(merchantId: string, itemId: string): void;
  updateQuantity(merchantId: string, itemId: string, quantity: number): void;
  clearCart(merchantId?: string): void;
  initiateCheckout(merchantId: string): Promise<CheckoutSession>;
  applyDiscount(sessionId: string, code: string): Promise<CheckoutSession>;
  selectFulfillment(sessionId: string, optionId: string): Promise<CheckoutSession>;
  selectPaymentMethod(sessionId: string, method: PaymentMethod): Promise<CheckoutSession>;
  completeCheckout(sessionId: string): Promise<OrderConfirmation>;
  cancelCheckout(sessionId: string): Promise<void>;
}
```

See [CHAT_SDK_TECHNICAL_SPEC.md §5](../../CHAT_SDK_TECHNICAL_SPEC.md#5-commerce-engine-specification) for full type definitions.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Checkout completion rate | >65% of initiated checkouts complete | Commerce funnel tracking |
| Cart-to-checkout conversion | >40% of carts reach checkout | Commerce funnel |
| Average checkout time | <3 minutes from initiation to confirmation | Timestamp analysis |
| Payment success rate | >95% of payment attempts succeed | Payment analytics |
| Commerce GMV through SDK | >$10M monthly by end of Phase 1 | Transaction tracking |

### Success Criteria

1. A user can add a product to cart, proceed through checkout (shipping, payment, confirmation), and receive an order confirmation — entirely within the chat thread — in under 3 minutes.
2. UCP's `requires_escalation` state seamlessly transitions to the Embedded Checkout Bridge (PRD-011) and returns the user to the conversation after completion.
3. Cart state persists across page refreshes (via session management) so users don't lose their cart.
4. The checkout flow correctly handles all UCP discount, loyalty, and fulfillment extensions.

---

## Critical User Journeys

### CUJ 1: End-to-End Purchase
**Actor:** Consumer shopping for a blender on Kroger's website
**Goal:** Purchase a blender entirely within the chat

1. User: "I'm looking for a blender under $100"
2. Agent shows product carousel with 4 blenders
3. User taps "Ninja Professional" → product details widget appears with price, rating, in-stock status
4. User: "Add this one to my cart"
5. Agent adds to cart → cart widget appears: "Ninja Professional - $79.99 | Qty: 1 | Total: $79.99"
6. User: "I'd like to check out"
7. Agent initiates UCP checkout → checkout flow widget renders:
   - Review: Ninja Professional, $79.99 + tax
   - Fulfillment: Standard shipping (free, 3-5 days) or Store pickup (today)
   - User selects "Store pickup at Kroger, Main St"
   - Payment: Google Pay (default, one-tap) or "Add a card"
   - User taps Google Pay → authenticates → payment processes
8. Order confirmation widget: "Order #KRG-123456 confirmed. Ready for pickup today at Kroger, Main St."
9. Chat continues: "Anything else I can help with?"

### CUJ 2: Discount Code Application
**Actor:** Consumer with a promo code
**Goal:** Apply a discount during checkout

1. User is on the Review step of checkout
2. User: "I have a promo code: SAVE20"
3. Agent calls `applyDiscount(sessionId, 'SAVE20')` via UCP
4. Checkout widget updates in real time: Subtotal $79.99 → Discount -$16.00 → Total $63.99
5. User sees the discount reflected before proceeding to payment

### CUJ 3: Cart Modification After Adding Items
**Actor:** Consumer changing their mind
**Goal:** Remove an item and change quantity of another

1. User has 3 items in cart
2. User: "Actually, remove the dish towels and I want 2 blenders instead of 1"
3. Agent updates cart → cart widget animates: dish towels removed, blender quantity changes to 2
4. Total updates in real time
5. User: "Looks good, let's check out"

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Commerce engine implements UCP's three-state checkout model | P0 |
| FR-2 | Cart widget renders current items with quantity controls and remove buttons | P0 |
| FR-3 | Cart updates emit `commerce:cart-updated` events in real time | P0 |
| FR-4 | Checkout flow widget renders multi-step inline checkout (review, fulfillment, payment, confirm) | P0 |
| FR-5 | Payment method selector shows available methods from UCP capability negotiation | P0 |
| FR-6 | Checkout state changes emit typed events (`checkout-started`, `checkout-state-changed`, etc.) | P0 |
| FR-7 | `requires_escalation` state triggers Embedded Checkout Bridge (PRD-011) | P0 |
| FR-8 | `applyDiscount()` calls UCP discount endpoint and updates checkout widget in real time | P1 |
| FR-9 | `selectFulfillment()` updates available options from UCP fulfillment extensions | P1 |
| FR-10 | Order confirmation widget renders order ID, items, delivery estimate, tracking URL | P0 |
| FR-11 | Cart state persists across page refreshes via session storage | P0 |
| FR-12 | Commerce engine is lazy-loaded (~25 KB) on first commerce event | P0 |
| FR-13 | All commerce events are captured by the Transaction Audit Trail (PRD-006) | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Commerce engine module is <25 KB gzipped | P0 |
| NFR-2 | Cart update round-trip (add/remove) completes in <500ms | P0 |
| NFR-3 | Checkout flow renders in <300ms (from initiation to first screen) | P0 |
| NFR-4 | Commerce widgets are fully accessible (keyboard, screen reader) per PRD-005 | P0 |
| NFR-5 | Commerce widgets render correctly on mobile per PRD-008 | P0 |

---

## Open Questions

1. **How do we handle multi-merchant carts in Phase 1?** Cross-merchant cart is Phase 2 (PRD-019). In Phase 1, should we only support single-merchant carts, or build the data model for multi-merchant and only enable single in the UI? Recommend: build the multi-merchant data model now (it's in the tech spec); restrict UI to single-merchant in Phase 1.

2. **What happens if checkout fails?** UCP doesn't define a retry protocol. Recommend: show inline error with "Try again" button; after 3 failures, offer alternative payment method or escalate to human.

3. **Should the cart persist across devices?** Cross-device cart requires server-side storage tied to user identity. Recommend: Phase 1 supports same-device persistence (session storage); cross-device is a Phase 2 enhancement tied to authenticated sessions.

4. **Tax calculation timing.** UCP returns taxes as part of the checkout session. Should we show estimated taxes in the cart widget (before checkout) or only in the checkout flow? Recommend: show "estimated tax" in cart with a note that final tax is calculated at checkout.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Commerce engine exposed via `chatSDK.getCommerce()`
- **Event Bus (PRD-002):** Commerce events flow through the bus
- **Widget Registry (PRD-003):** Commerce widgets registered in the registry
- **Accessibility (PRD-005):** Commerce widgets must be fully accessible
- **Audit Trail (PRD-006):** Commerce events must be audited
- **Mobile Design (PRD-008):** Commerce widgets must be mobile-responsive
- **AP2 Consent Flows (PRD-010):** Mandates required before payment
- **Embedded Checkout Bridge (PRD-011):** Handles `requires_escalation` state
- **Google Pay (PRD-012):** Default payment method
- **UCP backend:** Commerce API endpoints, merchant integration

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Commerce data model finalized | June 2026 Week 1 | Cart, checkout, payment types finalized |
| Cart widget working | July 2026 | Add/remove/modify items with real-time updates |
| Checkout flow working | August 2026 | Multi-step checkout end-to-end |
| Google Pay integrated | August 2026 Week 3 | Payment completes via Google Pay |
| Launch partner testing | September 2026 | End-to-end with Kroger or Lowe's |
| GA | September 2026 | Shipped with Phase 1 Commerce |
