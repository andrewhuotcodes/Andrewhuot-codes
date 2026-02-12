# PRD-012: Google Pay Integration

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q3 2026
**Pillar:** Protocol Commerce | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

Google Pay is the default payment method for UCP transactions. With 650M+ Gemini users and deep integration across Google's ecosystem, Google Pay offers the lowest-friction checkout path — users authenticate with biometrics (Face ID, fingerprint) or device PIN and complete payment in a single tap.

Integrating Google Pay directly into the Chat SDK's checkout flow eliminates the #1 source of checkout abandonment: manual payment entry. When the user reaches the payment step, they see a prominent "Pay with Google Pay" button. One tap, biometric confirmation, done.

---

## What Are We Building

A native Google Pay integration within the SDK's checkout flow widget, using the Google Pay API for Web. The integration handles payment sheet rendering, tokenization, and confirmation within the chat thread.

### User Flow

1. Checkout reaches payment step
2. SDK calls `google.payments.api.PaymentsClient.isReadyToPay()` to verify Google Pay availability
3. If available: Google Pay button renders as the primary payment option
4. User taps the button → Google Pay payment sheet opens (browser-native overlay)
5. User selects card and authenticates (biometrics or PIN)
6. Google Pay returns a payment token
7. SDK includes the token in the UCP `completeCheckout()` call
8. Payment processes → order confirmed

### Payment Sheet Configuration

```typescript
const paymentDataRequest = {
  apiVersion: 2,
  apiVersionMinor: 0,
  merchantInfo: {
    merchantId: config.googlePay.merchantId,
    merchantName: config.googlePay.merchantName,
  },
  allowedPaymentMethods: [{
    type: 'CARD',
    parameters: {
      allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
      allowedCardNetworks: ['VISA', 'MASTERCARD', 'AMEX', 'DISCOVER'],
    },
    tokenizationSpecification: {
      type: 'PAYMENT_GATEWAY',
      parameters: {
        gateway: 'google',        // UCP payment gateway
        gatewayMerchantId: merchantId,
      },
    },
  }],
  transactionInfo: {
    totalPriceStatus: 'FINAL',
    totalPrice: totals.total.amount.toString(),
    currencyCode: totals.total.currency,
    countryCode: 'US',            // from merchant config
  },
};
```

### Fallback Payment Methods

If Google Pay is not available (unsupported browser, no cards saved), the SDK falls back to:
1. Manual card entry form (rendered as a form widget)
2. Additional payment methods from UCP capability negotiation

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Google Pay availability rate | >60% of checkout sessions | `isReadyToPay()` success rate |
| Google Pay selection rate | >70% of users who see it select it | Payment analytics |
| Google Pay success rate | >95% of initiated Google Pay flows complete | Payment analytics |
| Time from button tap to confirmation | <10 seconds | Timestamp analysis |
| Overall checkout conversion lift | >15% vs. manual card entry | A/B testing (Phase 2) |

### Success Criteria

1. User taps Google Pay → authenticates → sees order confirmation — entire flow takes <10 seconds.
2. Google Pay button renders correctly in the chat widget on Chrome, Safari, Firefox, and Edge.
3. Google Pay works in both Shadow DOM and Iframe Sandbox modes.
4. Fallback to manual card entry works seamlessly when Google Pay is unavailable.

---

## Critical User Journeys

### CUJ 1: One-Tap Checkout with Google Pay
**Actor:** Consumer with Google Pay configured on their device
**Goal:** Pay for a purchase with minimal friction

1. User reaches payment step in the checkout flow widget
2. Prominent "Pay with Google Pay" button displayed (Google Pay brand guidelines compliant)
3. User taps the button
4. Browser-native Google Pay sheet appears showing saved cards
5. User selects Visa •••• 4242 and authenticates with fingerprint
6. Payment sheet closes → checkout flow shows "Processing payment..."
7. Payment succeeds → order confirmation widget renders
8. Total time: ~5 seconds from button tap to confirmation

### CUJ 2: Google Pay Not Available
**Actor:** Consumer using a browser without Google Pay support
**Goal:** Complete payment via manual card entry

1. User reaches payment step → SDK checks `isReadyToPay()`
2. Google Pay is not available (user has no saved cards or unsupported browser)
3. Payment step shows: card number, expiry, CVV fields (form widget)
4. User enters card details → processes payment
5. Order confirmed

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Check `isReadyToPay()` during checkout initiation and cache the result | P0 |
| FR-2 | Render Google Pay button per Google Pay brand guidelines | P0 |
| FR-3 | Google Pay button triggers `loadPaymentData()` with correct transaction info | P0 |
| FR-4 | Payment token from Google Pay is included in UCP `completeCheckout()` call | P0 |
| FR-5 | Payment success/failure is reflected in the checkout flow widget | P0 |
| FR-6 | Payment events (`payment-started`, `payment-completed`, `payment-failed`) are emitted | P0 |
| FR-7 | If Google Pay unavailable, fall back to card entry form | P0 |
| FR-8 | Google Pay configuration (merchant ID, environment) is set via `CommerceConfig` | P0 |
| FR-9 | Support TEST and PRODUCTION environments | P0 |
| FR-10 | AP2 Payment Mandate (PRD-010) is signed before Google Pay sheet opens | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Google Pay API loaded lazily (only when checkout reaches payment step) | P0 |
| NFR-2 | Works in both Shadow DOM and Iframe Sandbox modes | P0 |
| NFR-3 | Complies with Google Pay Web Brand Guidelines (button size, colors, placement) | P0 |
| NFR-4 | Payment token handling follows PCI DSS — token never logged or stored client-side | P0 |

---

## Open Questions

1. **Dynamic price updates.** If a discount is applied after the Google Pay button renders, the button shows the old amount until the sheet opens. Should we re-render the button with the updated amount? Recommend: yes, re-check transaction info on each render.

2. **Google Pay in iframe sandbox.** The Google Pay payment sheet is a browser-level popup. In iframe sandbox mode, `allow-popups` is set, but we need to verify the Google Pay sheet works correctly from within an iframe. Need cross-browser testing.

3. **Apple Pay support.** Should Phase 1 also include Apple Pay (via Payment Request API)? On iOS Safari, Apple Pay is the native payment method. Recommend: Apple Pay as a P1 Phase 2 item; Google Pay first.

---

## Dependencies

- **Commerce Engine (PRD-009):** Checkout flow triggers Google Pay
- **AP2 Consent Flows (PRD-010):** Payment Mandate signed before payment
- **Iframe Sandbox (PRD-007):** Google Pay must work in iframe mode
- **Google Pay API for Web:** External dependency

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Google Pay API integration | July 2026 | `isReadyToPay` + `loadPaymentData` working |
| Checkout flow integration | August 2026 | Google Pay renders in checkout widget |
| Cross-browser testing | August 2026 Week 3 | Chrome, Safari, Firefox, Edge verified |
| Iframe mode testing | September 2026 | Verified in iframe sandbox mode |
| GA | September 2026 | Shipped with Phase 1 Commerce |
