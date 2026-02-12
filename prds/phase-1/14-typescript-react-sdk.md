# PRD-014: TypeScript SDK + React SDK

**Phase:** 1 — "Make It Real" | **Priority:** P1 | **Quarter:** Q3 2026
**Pillar:** Developer Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

React is used by 40%+ of professional web developers. TypeScript is used by 78% of JavaScript developers. The current Chat SDK ships as an untyped JavaScript embed — no type definitions, no framework components, no IntelliSense. Developers integrating the SDK get zero editor assistance, no compile-time error checking, and no component abstractions for their framework of choice.

This PRD covers two deliverables shipped as separate npm packages:
1. **`@gecx/chat-sdk`** — fully typed TypeScript definitions for the core SDK
2. **`@gecx/chat-sdk-react`** — React components and hooks for declarative SDK integration

---

## What Are We Building

### TypeScript SDK (`@gecx/chat-sdk`)

A TypeScript type package that provides:
- Full type definitions for `ChatSDK`, `ChatSDKConfig`, `ChatEvent`, `ChatEventMap`, and all related interfaces
- JSDoc comments on every public method and property
- Type-safe event subscriptions (handler payload type inferred from event name)
- Exported type aliases for all widget data schemas, commerce types, and configuration

```typescript
import { ChatSDK, ChatSDKConfig } from '@gecx/chat-sdk';

const config: ChatSDKConfig = {
  deploymentId: 'projects/my-project/locations/us/agents/my-agent',
  language: 'en',
  auth: { type: 'token-broker', endpoint: '/api/auth/token' },
  sandboxMode: 'shadow-dom',
  commerce: {
    enableUCP: true,
    defaultCurrency: 'USD',
    googlePay: {
      merchantId: 'BCR2DN4T...',
      merchantName: 'My Store',
      environment: 'PRODUCTION',
    },
  },
};

const sdk = new ChatSDK();
await sdk.init(config);

// Type-safe event subscription — handler type is inferred
sdk.on('commerce:payment-completed', (event) => {
  // event.payload is typed as { orderId: string; amount: Money }
  console.log(event.payload.orderId);  // ✓ TypeScript knows this exists
  console.log(event.payload.foo);      // ✗ TypeScript error
});
```

### React SDK (`@gecx/chat-sdk-react`)

React components and hooks that provide declarative, idiomatic React integration:

**Components:**

- `<ChatProvider config={config}>` — initializes the SDK and provides context to child components
- `<ChatWidget>` — renders the pre-built chat widget with full UI
- `<ChatTrigger>` — renders a custom trigger element with chat state

**Hooks:**

- `useChatSDK()` — access the ChatSDK instance
- `useConversation()` — reactive access to messages, loading state, send methods
- `useCommerce()` — reactive access to cart state and commerce methods
- `useChatEvent(type, handler)` — subscribe to SDK events with automatic cleanup

```tsx
import { ChatProvider, ChatWidget, useChatSDK, useConversation, useCommerce } from '@gecx/chat-sdk-react';

function App() {
  return (
    <ChatProvider config={config} onReady={(sdk) => console.log('SDK ready')}>
      <ProductPage />
      <ChatWidget displayMode="floating" />
    </ChatProvider>
  );
}

function ProductPage() {
  const sdk = useChatSDK();
  const { cart, addToCart } = useCommerce();
  const { messages, isStreaming } = useConversation();

  return (
    <div>
      <button onClick={() => sdk.openWithMessage(`Tell me about product ${productId}`)}>
        Ask about this product
      </button>
      <span>Cart: {cart?.totalItems ?? 0} items</span>
    </div>
  );
}
```

See [CHAT_SDK_TECHNICAL_SPEC.md §8](../../CHAT_SDK_TECHNICAL_SPEC.md#8-react-sdk-specification) for full interface definitions.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| npm weekly downloads (@gecx/chat-sdk) | 5,000+ within 6 months of GA | npm stats |
| npm weekly downloads (@gecx/chat-sdk-react) | 2,000+ within 6 months | npm stats |
| TypeScript adoption rate | >60% of new integrations use TS types | Telemetry |
| React SDK adoption rate | >30% of new integrations use React SDK | Telemetry |
| Average integration time (React) | <1 hour | Developer survey |

### Success Criteria

1. A React developer can go from `npm install` to a working chat widget with commerce hooks in under 30 minutes.
2. TypeScript IntelliSense provides autocomplete for all SDK methods, config options, and event types.
3. The React SDK correctly handles component lifecycle — no memory leaks, no stale subscriptions, no double initialization.
4. Both packages are tree-shakeable — importing only `useChatSDK` doesn't bundle the entire commerce engine.

---

## Critical User Journeys

### CUJ 1: React Developer Integrates Chat into E-Commerce SPA
**Actor:** Frontend developer building a Next.js e-commerce site
**Goal:** Add chat with commerce capabilities to their existing React app

1. `npm install @gecx/chat-sdk-react`
2. Wraps app in `<ChatProvider config={config}>`
3. Drops `<ChatWidget />` into their layout component
4. Uses `useCommerce()` hook in their mini-cart component to sync cart state
5. Uses `useChatEvent('commerce:payment-completed')` to trigger their order confirmation page
6. Total integration time: ~45 minutes

### CUJ 2: TypeScript Developer Gets Compile-Time Safety
**Actor:** Backend-focused developer configuring the SDK
**Goal:** Avoid runtime errors via type checking

1. `npm install @gecx/chat-sdk`
2. Creates config object — TypeScript reports error: `auth` property is required
3. Adds auth — TypeScript reports error: `type` must be one of `'token-broker' | 'oauth2' | 'custom' | 'anonymous'`
4. Subscribes to `'commerce:payment-completd'` (typo) — TypeScript reports error: event type not in ChatEventMap
5. Every error caught at compile time, not at runtime in production

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | `@gecx/chat-sdk` exports TypeScript types for all public interfaces | P0 |
| FR-2 | All public methods have JSDoc comments explaining usage, parameters, and return types | P0 |
| FR-3 | Event subscription generics enforce correct payload types per event name | P0 |
| FR-4 | `@gecx/chat-sdk-react` exports `ChatProvider`, `ChatWidget`, `ChatTrigger` components | P0 |
| FR-5 | `ChatProvider` initializes SDK on mount, destroys on unmount | P0 |
| FR-6 | `useChatSDK()` returns the SDK instance from context | P0 |
| FR-7 | `useConversation()` returns reactive `messages`, `isLoading`, `isStreaming`, `sendMessage` | P0 |
| FR-8 | `useCommerce()` returns reactive `cart`, `activeCheckouts`, `addToCart`, `initiateCheckout` | P0 |
| FR-9 | `useChatEvent()` subscribes on mount, unsubscribes on unmount, respects deps array | P0 |
| FR-10 | Both packages are published to npm with correct `types`, `module`, and `main` fields | P0 |
| FR-11 | Both packages support tree-shaking (ESM exports, sideEffects: false) | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | `@gecx/chat-sdk` is types-only (0 KB runtime) | P0 |
| NFR-2 | `@gecx/chat-sdk-react` is <5 KB gzipped | P0 |
| NFR-3 | React SDK supports React 18+ and React 19 | P0 |
| NFR-4 | React SDK supports Next.js (SSR-compatible — no `window` access at import time) | P1 |
| NFR-5 | React SDK supports Strict Mode (no double-effect issues) | P0 |

---

## Open Questions

1. **Should we ship Vue, Angular, or Svelte SDKs?** React is the primary target given market share. Recommend: React in Phase 1; evaluate Vue/Svelte based on demand in Phase 2. The Web Components SDK (`@gecx/chat-sdk-elements`) provides framework-agnostic fallback.

2. **Next.js App Router compatibility.** The SDK initializes client-side. In Next.js App Router, components are server components by default. Recommend: `ChatProvider` and all hooks must be marked `'use client'`; document this clearly.

3. **Should hooks re-render on every message?** `useConversation()` returns `messages` — if this triggers a re-render on every streamed token, performance will suffer. Recommend: messages state updates on complete messages only; provide a separate `useStreamingMessage()` hook for real-time stream rendering.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Types mirror the core API
- **Event Bus (PRD-002):** `useChatEvent` wraps event subscriptions
- **Commerce Engine (PRD-009):** `useCommerce` wraps commerce methods

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| TypeScript type definitions complete | June 2026 | All interfaces typed and documented |
| React SDK components implemented | July 2026 | Provider, Widget, Trigger, all hooks |
| npm packages published (beta) | August 2026 | Available for partner preview |
| Next.js compatibility verified | August 2026 Week 3 | App Router + Pages Router tested |
| GA | September 2026 | Published to npm |
