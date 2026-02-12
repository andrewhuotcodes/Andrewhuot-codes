# PRD-024: Plugin Architecture

**Phase:** 2 — "Make It Intelligent" | **Priority:** P1 | **Quarter:** Q4 2026
**Pillar:** Developer Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The SDK v2 API and Widget Registry make the SDK programmable and extensible. But complex integrations — Shopify connectors, Salesforce CRM sync, loyalty program adapters — require coordinated event handling, context injection, and widget registration that's cumbersome to set up from scratch.

The Plugin Architecture provides a standard packaging format for reusable SDK extensions. A plugin bundles event handlers, widget registrations, context providers, and configuration into a single installable unit. Install a "Shopify Commerce" plugin and get Shopify-optimized widgets, Shopify cart sync, and Shopify-specific analytics — with one `registerPlugin()` call.

---

## What Are We Building

### Plugin Interface

```typescript
interface ChatPlugin {
  name: string;
  version: string;
  install(sdk: ChatSDK): void;
  uninstall?(): void;
}

// Example: Shopify Commerce Plugin
const shopifyPlugin: ChatPlugin = {
  name: 'shopify-commerce',
  version: '1.0.0',
  install(sdk) {
    // Register Shopify-branded widgets
    sdk.registerWidget(shopifyProductCard);
    sdk.registerWidget(shopifyCheckout);

    // Subscribe to events for Shopify analytics
    sdk.on('commerce:payment-completed', (event) => {
      shopifyAnalytics.trackPurchase(event.payload);
    });

    // Inject Shopify-specific context
    sdk.setContext('shopify_shop_id', config.shopId);
    sdk.setContext('shopify_customer_id', config.customerId);
  },
  uninstall() {
    // Clean up subscriptions and registrations
  },
};

// One-line installation
chatSDK.registerPlugin(shopifyPlugin);
```

### Plugin Capabilities

A plugin can:
- Register custom widgets via `sdk.registerWidget()`
- Subscribe to events via `sdk.on()`
- Set context values via `sdk.setContext()`
- Register proactive engagement triggers
- Track custom analytics events
- Extend the commerce engine with custom payment methods

A plugin cannot:
- Modify the SDK's internal state directly
- Override core SDK methods
- Access other plugins' internal state
- Execute code outside the event bus lifecycle

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Plugins in production | 10+ unique plugins across all deployments | Plugin telemetry |
| Plugin install rate | >20% of deployments use at least 1 plugin | Deployment analysis |
| Average plugins per deployment | 1.5+ (for deployments using plugins) | Deployment analysis |

### Success Criteria

1. A developer can create a plugin, test it in isolation, and publish it — and another developer can install it with `registerPlugin()` in one line.
2. Plugin errors are isolated — a throwing plugin does not crash the SDK.
3. At least 3 official plugins ship with Phase 2: Shopify Commerce, Google Analytics 4, and CRM Webhook.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | `registerPlugin()` accepts a ChatPlugin object and calls `install()` | P0 |
| FR-2 | Plugins have access to the full public ChatSDK API | P0 |
| FR-3 | Plugin errors are caught and do not crash the SDK | P0 |
| FR-4 | `uninstall()` is called on `sdk.destroy()` for cleanup | P0 |
| FR-5 | Multiple plugins can be registered; execution order matches registration order | P0 |
| FR-6 | Plugin name uniqueness enforced (no duplicate names) | P1 |
| FR-7 | 3 official plugins shipped: Shopify Commerce, GA4, CRM Webhook | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Plugin architecture adds <1 KB to core bundle | P0 |
| NFR-2 | Plugin loading is synchronous (no async install to avoid race conditions) | P0 |

---

## Open Questions

1. **Plugin distribution.** Should plugins be published to npm or to a custom registry? Recommend: npm (standard ecosystem). Official plugins under `@gecx/plugin-*` namespace.
2. **Plugin permissions.** Should plugins declare required capabilities? Recommend: Phase 3 enhancement. Phase 2 plugins have full SDK access.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Plugin registration method
- **Widget Registry (PRD-003):** Plugins register widgets
- **Event Bus (PRD-002):** Plugins subscribe to events

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Plugin interface finalized | September 2026 | ChatPlugin interface and lifecycle |
| Plugin error isolation | October 2026 | Throwing plugins don't crash SDK |
| Official plugins (3) | November 2026 | Shopify, GA4, CRM Webhook |
| GA | December 2026 | Shipped with Phase 2 |
