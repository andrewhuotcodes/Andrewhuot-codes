# PRD-007: Iframe Sandbox Mode

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Trust | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The current Chat SDK renders inside a Shadow DOM attached to the host page. While Shadow DOM provides style encapsulation, it does not provide script isolation. The SDK's JavaScript runs in the same execution context as the host page, shares `localStorage`, and has access to the host page's DOM. The official documentation includes a warning about XSS risks in this configuration.

For enterprise deployments handling sensitive data — financial services, healthcare, government — this is a security blocker. A compromised host page (or a third-party script injected into it) could read conversation content, intercept authentication tokens, or manipulate commerce flows.

Iframe Sandbox Mode provides strict isolation: the SDK renders inside a cross-origin iframe with configurable sandbox attributes. The host page communicates with the SDK exclusively via `postMessage`, with a typed message protocol and origin validation.

---

## What Are We Building

An optional deployment mode where the entire Chat SDK renders inside a sandboxed iframe instead of a Shadow DOM. The iframe is loaded from a Google-hosted origin (separate from the host page), providing true cross-origin isolation.

### Architecture

```
Host Page (merchant.com)                 SDK Iframe (chat.gecx.cloud)
┌───────────────────────┐               ┌───────────────────────┐
│                       │               │                       │
│  chatSDK.open()  ────►│── postMessage ─►│  Widget renders here  │
│  chatSDK.on()    ◄────│◄─ postMessage ──│  Events fire here     │
│                       │               │  Commerce runs here   │
│  Host page scripts    │   ISOLATED    │                       │
│  cannot access ──────►│◄─────────────►│  SDK scripts cannot   │
│  iframe content       │               │  access host page     │
│                       │               │                       │
└───────────────────────┘               └───────────────────────┘
```

### Isolation Guarantees

| Threat | Shadow DOM (current) | Iframe Sandbox |
|--------|---------------------|----------------|
| Host page reads chat content | Possible | Blocked by same-origin policy |
| Host page intercepts auth tokens | Possible (shared JS context) | Blocked |
| Third-party script XSS | Chat content vulnerable | Chat content isolated |
| SDK reads host page DOM | Possible | Blocked |
| Shared localStorage | Yes (same origin) | No (different origin) |
| Shared cookies | Yes | No (unless explicitly shared) |

### Iframe Sandbox Attributes

```html
<iframe
  src="https://chat.gecx.cloud/v2/widget?deployment=..."
  sandbox="allow-scripts allow-forms allow-popups allow-same-origin"
  allow="camera; microphone; payment; geolocation"
  referrerpolicy="strict-origin"
  loading="lazy"
></iframe>
```

The `sandbox` attribute restricts the iframe. Notably:
- `allow-scripts`: Required for the SDK JavaScript
- `allow-forms`: Required for checkout flows
- `allow-popups`: Required for Google Pay popup flow
- `allow-same-origin`: Required for SDK to access its own cookies/storage
- **Not included:** `allow-top-navigation` (SDK cannot navigate the host page)

### Host ↔ Iframe Communication Protocol

All communication uses `postMessage` with strict origin validation and typed messages:

```typescript
// Host → Iframe messages
type HostMessage =
  | { type: 'sdk:init'; config: ChatSDKConfig }
  | { type: 'sdk:open' }
  | { type: 'sdk:close' }
  | { type: 'sdk:send-message'; text: string; metadata?: Record<string, unknown> }
  | { type: 'sdk:set-context'; key: string; value: unknown }
  | { type: 'sdk:set-identity'; identity: UserIdentity }
  | { type: 'sdk:set-language'; languageCode: string }
  | { type: 'sdk:register-widget'; definition: SerializedWidgetDefinition };

// Iframe → Host messages
type IframeMessage =
  | { type: 'sdk:ready' }
  | { type: 'sdk:event'; event: ChatEvent<unknown> }
  | { type: 'sdk:resize'; height: number }
  | { type: 'sdk:request-focus' }
  | { type: 'sdk:navigation'; url: string };
```

### Developer Experience

From the developer's perspective, the API is identical regardless of sandbox mode. The `ChatSDK` interface works the same — method calls are transparently proxied via `postMessage` in iframe mode.

```javascript
// Configuration — only difference is one config key
const chatSDK = new ChatSDK({
  deploymentId: 'projects/my-project/...',
  sandboxMode: 'iframe',  // ← this is the only change
  // ... rest of config identical
});

// All API calls work identically
chatSDK.open();
chatSDK.setContext('product_id', 'SKU-123');
chatSDK.on('commerce:payment-completed', handler);
```

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Enterprise adoption of iframe mode | >50% of financial/healthcare/gov deployments | Deployment config tracking |
| Security incidents via SDK | 0 critical/high | Security monitoring |
| Performance overhead vs Shadow DOM | <200ms additional init time | Performance comparison testing |
| Iframe communication latency | P99 <5ms per message round-trip | postMessage timing |

### Success Criteria

1. A penetration test by Google's security team confirms that a compromised host page cannot access chat content, auth tokens, or commerce data in iframe mode.
2. The API behavior is identical between Shadow DOM and iframe modes — all integration tests pass in both modes without modification.
3. Google Pay checkout works correctly within the iframe (popup flow).
4. CSP-strict enterprise environments can deploy iframe mode without CSP modifications to their host page.

---

## Critical User Journeys

### CUJ 1: Financial Services Deployment
**Actor:** Security engineer at a bank
**Goal:** Deploy the chat widget on their banking portal with strict isolation

1. Security team reviews SDK deployment options
2. Selects `sandboxMode: 'iframe'` for cross-origin isolation
3. Verifies that the iframe is loaded from `chat.gecx.cloud` (separate origin from their domain)
4. Confirms that no SDK JavaScript executes in their origin's context
5. Confirms that their CSP does not need to allow `unsafe-eval` or `unsafe-inline`
6. Pen test verifies: injecting a `<script>` tag on the host page cannot read chat conversation content
7. Deploys to production

### CUJ 2: Commerce Checkout in Iframe Mode
**Actor:** End user completing a purchase
**Goal:** Full checkout experience works within the sandboxed iframe

1. User browses products, adds to cart
2. Initiates checkout — checkout flow widget renders inside the iframe
3. Selects Google Pay — popup window opens (allowed by `allow-popups`)
4. Completes payment in popup → popup closes → iframe receives confirmation
5. Order confirmation widget renders inside iframe
6. Host page receives `commerce:payment-completed` event via postMessage

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | SDK supports `sandboxMode: 'iframe'` configuration option | P0 |
| FR-2 | In iframe mode, SDK renders inside a cross-origin iframe from `chat.gecx.cloud` | P0 |
| FR-3 | Host page SDK proxy transparently forwards all API calls via postMessage | P0 |
| FR-4 | Iframe SDK sends all events back to host via postMessage | P0 |
| FR-5 | All postMessage communication validates origin (both directions) | P0 |
| FR-6 | Iframe auto-resizes based on content height | P0 |
| FR-7 | Google Pay popup checkout works from within the iframe | P0 |
| FR-8 | Embedded merchant checkout (requires_escalation) works within iframe | P0 |
| FR-9 | Custom widget registration works across the iframe boundary (serialized definitions) | P1 |
| FR-10 | Shadow DOM mode remains the default (no breaking change) | P0 |
| FR-11 | Focus management works across the iframe boundary | P0 |
| FR-12 | Keyboard navigation (Escape to close) works from within the iframe | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Host-page proxy (postMessage bridge) is <5 KB gzipped | P0 |
| NFR-2 | postMessage round-trip latency <5ms (P99) | P0 |
| NFR-3 | Iframe mode does not require CSP changes on the host page (beyond frame-src) | P0 |
| NFR-4 | No `eval()`, `new Function()`, or `document.write()` in SDK code | P0 |
| NFR-5 | All communication is serializable (no function passing across iframe boundary) | P0 |

---

## Open Questions

1. **How do custom widgets work across the iframe boundary?** Widget render functions are JavaScript functions — they can't be serialized via postMessage. Options: (a) custom widgets always run on the host side with a portal into the iframe, (b) custom widgets are loaded as separate script URLs inside the iframe, (c) custom widgets only work in Shadow DOM mode. Recommend: (b) — widget definitions include a `scriptUrl` that the iframe fetches and executes.

2. **How does theming work?** Host page CSS custom properties don't cross the iframe boundary. Recommend: theme tokens are passed as part of the `sdk:init` message and applied inside the iframe.

3. **What about service workers?** If the host page has a service worker, it won't intercept iframe requests (different origin). This affects offline behavior. Recommend: SDK iframe has its own service worker for offline support.

4. **Performance overhead on mobile?** Iframes have higher memory overhead than Shadow DOM on mobile devices. Need to benchmark on low-end Android devices. Recommend: Shadow DOM remains default; iframe mode is opt-in for security-sensitive deployments.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Proxy layer must implement the full ChatSDK interface
- **Widget Registry (PRD-003):** Cross-iframe widget registration
- **Accessibility (PRD-005):** Focus management across iframe boundary
- **Google Pay integration (PRD-012):** Popup flow from iframe

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| postMessage protocol defined | April 2026 Week 2 | Message types and origin validation finalized |
| Host-side proxy implemented | May 2026 | All ChatSDK methods proxied via postMessage |
| Iframe-side receiver implemented | May 2026 Week 3 | Full SDK running inside iframe |
| Security pen test | June 2026 | Google security team validates isolation |
| GA with SDK v2 | July 2026 | Available as opt-in config |
