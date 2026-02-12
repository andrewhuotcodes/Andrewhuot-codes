# PRD-001: SDK v2 Core API

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Developer Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The current Chat SDK exposes two JavaScript methods (`renderCustomText`, `renderCustomCard`) and four events (`loaded`, `close`, `error`, `cart-count`). This is insufficient for any integration beyond "embed and forget." Developers cannot programmatically control the widget, listen to conversation events, inject page context, manage sessions, or build host-page integrations.

The SDK v2 Core API is the single most critical feature in the entire roadmap. Every other feature — commerce, widgets, analytics, multi-agent — depends on having a programmable surface. Without it, the Chat SDK remains a black box that happens to live on a web page.

---

## What Are We Building

A complete JavaScript API that gives developers full programmatic control of the Chat SDK. The API covers five domains:

### 1. Lifecycle Control
Developers can open, close, minimize, maximize, reset, and destroy the widget programmatically. This enables contextual triggers (open chat when user clicks a "Get help" link), proactive engagement (open chat after 30 seconds on a product page), and SPA integration (destroy and reinitialize when the user navigates).

### 2. Messaging
Developers can send messages on behalf of the user, send structured actions (button clicks, form submissions), and inject agent-side messages (system notifications, promotional nudges). This enables host-page-driven conversations where the surrounding application provides context to the chat.

### 3. Context Management
Developers can set key-value context pairs that are automatically sent to the agent with every message. This enables page-aware conversations — the agent knows which product the user is viewing, their cart state, their loyalty tier, and their language preference without the user having to explain.

### 4. Session Management
Developers can get the current session ID, restore previous sessions, access conversation history, and clear history. This enables cross-session continuity (user returns next week and picks up where they left off) and multi-device scenarios (user starts on mobile, continues on desktop).

### 5. Event Subscription
Developers can subscribe to 30+ typed events across message lifecycle, conversation lifecycle, widget interactions, commerce actions, typing indicators, display state changes, and errors. This enables analytics, custom workflows, CRM integrations, and real-time monitoring.

### API Surface

```typescript
interface ChatSDK {
  // Lifecycle
  init(config: ChatSDKConfig): Promise<void>;
  open(): void;
  close(): void;
  minimize(): void;
  destroy(): void;
  reset(): Promise<void>;
  readonly initialized: boolean;
  readonly isOpen: boolean;

  // Messaging
  sendMessage(text: string, metadata?: Record<string, unknown>): Promise<Message>;
  sendAction(actionId: string, payload: unknown): Promise<void>;
  renderText(text: string): void;
  renderWidget(widgetType: string, data: unknown): void;

  // Context
  setContext(key: string, value: unknown): void;
  getContext(key: string): unknown;
  setUserIdentity(identity: UserIdentity): void;
  getUserIdentity(): UserIdentity | null;
  setLanguage(languageCode: string): void;

  // Session
  getSessionId(): string | null;
  getConversationId(): string | null;
  getHistory(): Promise<Message[]>;
  restoreSession(sessionId: string): Promise<void>;
  clearHistory(): Promise<void>;

  // Events
  on<K extends keyof ChatEventMap>(type: K, handler: (event: ChatEvent<ChatEventMap[K]>) => void): () => void;
  onAny(handler: (event: ChatEvent<unknown>) => void): () => void;
  once<K extends keyof ChatEventMap>(type: K, handler: (event: ChatEvent<ChatEventMap[K]>) => void): () => void;

  // Widgets
  registerWidget<TData, TAction>(definition: WidgetDefinition<TData, TAction>): void;
  unregisterWidget(type: string): void;

  // Plugins
  registerPlugin(plugin: ChatPlugin): void;

  // Analytics
  trackEvent(name: string, properties?: Record<string, unknown>): void;

  // Deep Linking
  openWithMessage(text: string): void;
  openWithContext(context: Record<string, unknown>): void;
}
```

See [CHAT_SDK_TECHNICAL_SPEC.md §7](../../CHAT_SDK_TECHNICAL_SPEC.md#7-public-sdk-api) for full interface definitions.

### Backward Compatibility

The v2 API is additive. The existing `renderCustomText()` and `renderCustomCard()` methods continue to work and are internally mapped to `chatSDK.renderText()` and `chatSDK.renderWidget('custom_card', data)`. Existing v1 embed codes continue to function without changes. New methods are available immediately after upgrading the script tag to the v2 CDN endpoint.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| API adoption rate | 50+ enterprise deployments using v2 methods within 90 days of GA | Deployment telemetry |
| Average API methods used per deployment | >5 methods (beyond init/open/close) | SDK analytics |
| Developer NPS | >40 | Quarterly developer survey |
| Time-to-first-integration | <2 hours from reading docs to first working API call | Developer onboarding study |
| v1 → v2 migration rate | >80% of active deployments within 6 months | Version tracking |
| API error rate | <0.1% of API calls result in SDK errors | Error telemetry |

### Success Criteria

1. A developer with no prior GECX experience can go from zero to a working integration (open widget, send a context-aware message, listen to a response event) in under 2 hours using only the documentation.
2. The top 5 integration partners (Kroger, Lowe's, Papa Johns, etc.) confirm the API meets their integration requirements without workarounds.
3. Zero breaking changes to existing v1 deployments after the upgrade.

---

## Critical User Journeys

### CUJ 1: E-Commerce Product Page Integration
**Actor:** Frontend developer at a retailer
**Goal:** Open the chat widget pre-loaded with product context when the user clicks "Ask about this product"

```javascript
// On product page load
chatSDK.setContext('product_id', 'SKU-12345');
chatSDK.setContext('product_name', 'Samsonite Carry-On 22"');
chatSDK.setContext('product_price', '$249.99');
chatSDK.setContext('page_type', 'product_detail');

// When user clicks the "Ask about this product" button
document.getElementById('ask-btn').addEventListener('click', () => {
  chatSDK.openWithMessage('Tell me more about this suitcase');
});

// Track when the agent recommends adding to cart
chatSDK.on('commerce:cart-updated', (event) => {
  updateMiniCartBadge(event.payload.cart.totalItems);
});
```

### CUJ 2: Cross-Session Continuity
**Actor:** Returning customer
**Goal:** Resume a conversation from a previous visit

```javascript
// On page load, check for a saved session
const savedSessionId = localStorage.getItem('gecx_session_id');
if (savedSessionId) {
  await chatSDK.restoreSession(savedSessionId);
  // Widget shows previous conversation history
}

// Save session ID when conversation starts
chatSDK.on('session:started', (event) => {
  localStorage.setItem('gecx_session_id', event.payload.sessionId);
});
```

### CUJ 3: Analytics Pipeline Integration
**Actor:** Data engineer at an enterprise customer
**Goal:** Stream all conversation events to their analytics warehouse

```javascript
// Subscribe to all events for analytics
chatSDK.onAny((event) => {
  analyticsSDK.track(event.type, {
    sessionId: event.sessionId,
    timestamp: event.timestamp,
    ...event.payload,
  });
});
```

### CUJ 4: SPA Navigation Handling
**Actor:** React developer building a single-page app
**Goal:** Maintain chat state across client-side route changes without duplication

```javascript
// In the root App component — initialize once
useEffect(() => {
  chatSDK.init({ deploymentId: 'projects/my-project/...' });
  return () => chatSDK.destroy();
}, []);

// On route change — update context, don't reinitialize
useEffect(() => {
  chatSDK.setContext('current_page', router.pathname);
  chatSDK.setContext('page_category', getCategory(router.pathname));
}, [router.pathname]);
```

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | SDK exposes `init()` that accepts a typed configuration object and returns a Promise | P0 |
| FR-2 | SDK exposes `open()`, `close()`, `minimize()`, `destroy()`, `reset()` lifecycle methods | P0 |
| FR-3 | SDK exposes `sendMessage()` that sends user text and returns the created Message | P0 |
| FR-4 | SDK exposes `sendAction()` for structured interaction payloads (button clicks, etc.) | P0 |
| FR-5 | SDK exposes `renderText()` and `renderWidget()` for injecting agent-side content | P0 |
| FR-6 | SDK exposes `setContext()` / `getContext()` for page-level context injection | P0 |
| FR-7 | SDK exposes `setUserIdentity()` for authenticated user context | P0 |
| FR-8 | SDK exposes `setLanguage()` to change conversation language at runtime | P0 |
| FR-9 | SDK exposes `getSessionId()`, `getConversationId()` | P0 |
| FR-10 | SDK exposes `getHistory()` returning a Promise of Message[] | P1 |
| FR-11 | SDK exposes `restoreSession()` accepting a previous session ID | P1 |
| FR-12 | SDK exposes `on()`, `once()`, `onAny()` event subscription methods returning unsubscribe functions | P0 |
| FR-13 | All 30+ event types in the ChatEventMap are emitted at the correct lifecycle points | P0 |
| FR-14 | SDK exposes `registerWidget()` and `unregisterWidget()` for custom widget types | P0 |
| FR-15 | SDK exposes `registerPlugin()` for plugin installation | P1 |
| FR-16 | SDK exposes `trackEvent()` for custom analytics events | P1 |
| FR-17 | SDK exposes `openWithMessage()` and `openWithContext()` for deep linking | P1 |
| FR-18 | Existing v1 methods (`renderCustomText`, `renderCustomCard`) continue to work unchanged | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Core API module adds <30 KB gzipped to the bundle | P0 |
| NFR-2 | `init()` completes in <200ms on a median mobile device (Moto G Power) | P0 |
| NFR-3 | Event emission latency <1ms from trigger to handler invocation | P0 |
| NFR-4 | API is fully tree-shakeable — unused methods are eliminated by bundlers | P1 |
| NFR-5 | All public methods have JSDoc comments and TypeScript type definitions | P0 |
| NFR-6 | API surface is compatible with all major browsers (Chrome 90+, Firefox 90+, Safari 15+, Edge 90+) | P0 |
| NFR-7 | Multiple `ChatSDK` instances can coexist on the same page (multi-widget support) | P1 |
| NFR-8 | Thread-safe event emission — handlers cannot block the main thread for >16ms | P0 |

---

## Open Questions

1. **Should `sendMessage()` be fire-and-forget or return the agent's response?** Currently spec'd to return the user's Message object. Returning the agent response would require waiting for the full response stream, which could take seconds. Recommend: return user message immediately; use events for agent response.

2. **How do we handle `init()` being called twice?** Options: throw an error, silently no-op, or destroy and reinitialize. Recommend: console warning + no-op, with explicit `destroy()` required before re-init.

3. **Should context values be typed or `unknown`?** Typed context (via generics) provides better DX but requires schema definition. Recommend: `unknown` for v2.0, typed context API as a follow-up.

4. **How does the API interact with Content Security Policy?** Sites with strict CSP may block inline styles/scripts. Need to support CSP nonce passing and ensure no `eval()` usage.

5. **What's the migration story for customers using the Dialogflow CX Messenger (`<df-messenger>`) web component?** Need to clarify if v2 replaces df-messenger entirely or runs alongside it.

---

## Dependencies

- **Event Bus (PRD-002):** The `on()`, `once()`, `onAny()` methods delegate to the Event Bus
- **Widget Registry (PRD-003):** `registerWidget()` delegates to the Widget Registry
- **Conversation History API (PRD-015):** `getHistory()` and `restoreSession()` require persistent storage
- **GECX backend:** Session management, message routing, and agent connectivity

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| API Design Review | April 2026 Week 1 | Final API surface approved by SDK team + key partners |
| Alpha (internal) | May 2026 | Core lifecycle + messaging + events working end-to-end |
| Beta (partner preview) | June 2026 | Full API available to 3 launch partners |
| GA | July 2026 | Public release with documentation site |
