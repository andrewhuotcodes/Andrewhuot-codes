# PRD-019: Cross-Merchant Cart

**Phase:** 2 — "Make It Intelligent" | **Priority:** P0 | **Quarter:** Q4 2026
**Pillar:** Protocol Commerce | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

When a shopping agent compares products across retailers — "Compare the Ninja blender from Kroger, the Vitamix from Target, and the KitchenAid from Walmart" — the user should be able to add items from multiple merchants to a single cart. This is the Shopping Graph monetization play: Google's unique position is cross-merchant product intelligence, and the cross-merchant cart makes that intelligence actionable.

UCP checkout sessions are per-merchant — you cannot have a single checkout session spanning Walmart and Target. The cross-merchant cart is a client-side convenience abstraction that presents a unified cart experience while managing separate per-merchant checkout sessions behind the scenes.

---

## What Are We Building

A unified cart that aggregates items from multiple merchants with intelligent per-merchant checkout orchestration.

### Cart Architecture

```
┌──────────────────────────────────────┐
│ Unified Cart                          │
│                                       │
│ ┌─────────────────────────────────┐  │
│ │ Kroger                          │  │
│ │ Ninja Blender         $79.99   │  │
│ │ Kitchen Towels (x2)    $9.98   │  │
│ │ Subtotal:             $89.97   │  │
│ │ [Checkout with Kroger]          │  │
│ └─────────────────────────────────┘  │
│                                       │
│ ┌─────────────────────────────────┐  │
│ │ Target                          │  │
│ │ Vitamix E310          $349.99  │  │
│ │ Subtotal:             $349.99  │  │
│ │ [Checkout with Target]          │  │
│ └─────────────────────────────────┘  │
│                                       │
│ ───────────────────────────────────  │
│ Total (2 merchants):    $439.96     │
│ [Checkout All]                       │
└──────────────────────────────────────┘
```

### "Checkout All" Flow

When the user clicks "Checkout All," the SDK orchestrates sequential per-merchant checkouts:

1. Start checkout with Merchant 1 (Kroger)
2. Present mandate → user signs → complete payment
3. Show confirmation for Merchant 1
4. Start checkout with Merchant 2 (Target)
5. Present mandate → user signs → complete payment
6. Show combined confirmation summary

Each merchant checkout is a complete UCP (or ACP) session. The user sees a progress indicator: "Checkout 1 of 2 — Kroger" then "Checkout 2 of 2 — Target."

### Per-Merchant Checkout

Users can also check out with individual merchants by tapping the per-merchant "Checkout with [Merchant]" button, leaving items from other merchants in the cart for later.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Cross-merchant carts created | 10K+ daily | Commerce analytics |
| Average merchants per cart | 1.8+ | Cart analytics |
| "Checkout All" completion rate | >50% of initiated multi-merchant checkouts complete all merchants | Commerce funnel |
| Cross-merchant cart GMV | >15% of total SDK GMV | Transaction tracking |

### Success Criteria

1. A user adds products from 3 different retailers, reviews a unified cart with per-merchant subtotals, and checks out with all 3 sequentially in one session.
2. Cart state persists across page refreshes and session restores.
3. If one merchant's checkout fails, the others still succeed and the failed checkout can be retried.

---

## Critical User Journeys

### CUJ 1: Comparison Shopping Across Retailers
**Actor:** Budget-conscious consumer
**Goal:** Find the best deal across multiple stores

1. User: "I need a blender, toaster, and coffee maker — find me the best prices"
2. Agent uses Shopping Graph to compare across Kroger, Target, Walmart
3. Agent recommends: blender from Kroger ($79), toaster from Target ($45), coffee maker from Walmart ($89)
4. User: "Add all three to my cart"
5. Cart widget shows 3 merchant sections with per-merchant subtotals
6. Total: $213
7. User: "Check out"
8. Sequential checkout: Kroger ($79) → Target ($45) → Walmart ($89)
9. Combined confirmation: 3 orders placed, 3 tracking numbers

### CUJ 2: Partial Checkout
**Actor:** User who wants to buy from one merchant now and decide on others later
**Goal:** Check out with one merchant without losing the rest of the cart

1. Cart has items from Kroger and Target
2. User: "Just check out with Kroger for now"
3. Kroger checkout completes → Kroger items removed from cart
4. Target items remain in cart for later
5. User can return tomorrow and check out with Target

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Cart supports items from multiple merchants, grouped by merchant | P0 |
| FR-2 | Cart widget displays per-merchant sections with subtotals and a combined total | P0 |
| FR-3 | "Checkout All" initiates sequential per-merchant checkout sessions | P0 |
| FR-4 | Per-merchant "Checkout with [Name]" buttons allow individual checkout | P0 |
| FR-5 | Progress indicator shows "Checkout 1 of N — [Merchant Name]" | P0 |
| FR-6 | If one merchant checkout fails, others can still proceed | P0 |
| FR-7 | Combined confirmation summary after all checkouts complete | P0 |
| FR-8 | Completed merchant items are removed from cart; unchecked merchants remain | P0 |
| FR-9 | Cart persists across page refreshes | P0 |
| FR-10 | Works with both UCP and ACP merchants in the same cart | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Cart UI updates in <200ms when items are added/removed | P0 |
| NFR-2 | Supports up to 10 merchants per cart (practical limit) | P0 |
| NFR-3 | Mobile: per-merchant sections stack vertically with collapsible headers | P0 |

---

## Open Questions

1. **Parallel vs. sequential checkout.** Could we open multiple checkout sessions simultaneously (in tabs or stacked)? Recommend: sequential for Phase 2 (simpler, clearer UX). Parallel as Phase 3 optimization.

2. **Unified shipping.** If the user buys from Kroger and Target, they need to enter their shipping address twice (once per checkout). Could we pre-fill the second checkout's address? Recommend: yes, remember the address from the first checkout and pre-fill subsequent ones.

3. **Price changes between cart creation and checkout.** Prices may change between when the user adds to cart and when they check out. Recommend: re-verify prices at checkout initiation. If prices changed, show the difference before the mandate.

---

## Dependencies

- **Commerce Engine (PRD-009):** Multi-merchant CartState data model
- **UCP Checkout (PRD-009):** Per-merchant checkout sessions
- **ACP Layer (PRD-018):** ACP merchants in the same cart
- **AP2 Mandates (PRD-010):** Per-merchant mandates

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Multi-merchant cart UI | October 2026 | Cart widget with merchant sections |
| Sequential checkout orchestration | November 2026 | "Checkout All" with progress indicator |
| Combined confirmation | November 2026 Week 3 | Summary after all checkouts |
| GA | December 2026 | Shipped with Phase 2 |
