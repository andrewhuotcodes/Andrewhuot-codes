# PRD-003: Widget Registry

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Extensible Widgets | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The current SDK ships five fixed widget types: Product Carousel, Product Details, Product Comparison, Order Summary, and Quick Actions. These cover basic e-commerce scenarios but block every other vertical — healthcare forms, financial calculators, appointment scheduling, document collection, insurance quotes, travel booking. There is no mechanism for developers to create custom widget types, and any new widget requires a SDK release.

The Widget Registry transforms the SDK from a fixed set of UI components into an extensible rendering platform. Agents declare UI intent via structured JSON; the registry resolves that intent to a registered renderer; the renderer produces interactive, accessible, themed UI inside a sandboxed container. Built-in widgets use the exact same registration API as third-party widgets — no privileged internal APIs.

This is the architectural heart of the "declarative surface" concept described in the [vision paper](../../CHAT_SDK_VISION_2026.md).

---

## What Are We Building

### The Registration API

Developers register widget types by providing a definition object with a type name, a JSON schema for data validation, a render function, and required accessibility metadata.

```typescript
chatSDK.registerWidget({
  type: 'appointment_scheduler',
  version: '1.0.0',
  schema: appointmentSchema,            // JSON Schema for validation
  render: (container, data, context) => {
    // Render calendar UI into container
    // context provides theme, locale, direction, viewport, emit()
    return () => { /* cleanup */ };
  },
  accessibility: {
    role: 'dialog',
    label: (data) => `Schedule appointment with ${data.providerName}`,
    announceOnRender: (data) => `Appointment scheduler opened for ${data.providerName}`,
  },
  supportsStreaming: false,
  estimatedHeight: 400,
});
```

### Resolution Logic

When an agent emits a widget intent:

1. **Lookup:** Registry checks if a widget with the given type is registered
2. **Validate:** Data is validated against the widget's JSON schema
3. **Render:** Widget's render function is called with a sandboxed container, validated data, and context
4. **Fallback:** If no widget is registered for the type, the registry invokes the fallback renderer (Generative UI in Phase 2; error card in Phase 1)

### 12 Built-In Widgets

All shipped as standard registrations — overridable by merchants who want branded experiences.

| Widget Type | Description | Vertical |
|-------------|-------------|----------|
| `product_carousel` | Horizontal scrollable product cards | Commerce |
| `product_details` | Single product detail view with images, price, variants | Commerce |
| `product_comparison` | Side-by-side comparison table | Commerce |
| `order_summary` | Line items, totals, discounts, fulfillment | Commerce |
| `quick_actions` | Horizontal/vertical/grid button group | General |
| `checkout_flow` | Multi-step checkout (review → fulfillment → payment → confirm) | Commerce |
| `cart_view` | Current cart contents with modify/remove | Commerce |
| `fulfillment_picker` | Shipping/pickup/delivery window selector | Commerce |
| `form` | Dynamic form with validation (text, email, phone, select, date, address) | General |
| `mandate_card` | AP2 mandate presentation with sign/reject | Commerce |
| `order_tracking` | Post-purchase status timeline | Commerce |
| `rating_review` | Star rating with optional text feedback | General |

### Widget Context

Every widget render receives a `WidgetContext` with everything needed for consistent rendering:

- **theme:** CSS custom properties for colors, typography, spacing, elevation
- **locale:** BCP 47 language tag (e.g., `'ja-JP'`)
- **direction:** `'ltr'` or `'rtl'`
- **viewport:** `'mobile'` | `'tablet'` | `'desktop'` plus pixel width
- **emit():** Send interaction events back to the Event Bus
- **t():** Localized string lookup for built-in labels
- **cspNonce:** For sites with strict Content Security Policy

### Lazy Loading

Widget renderers can be async, enabling code splitting:

```typescript
chatSDK.registerWidget({
  type: 'checkout_flow',
  version: '1.0.0',
  schema: checkoutFlowSchema,
  render: async (container, data, ctx) => {
    const { renderCheckout } = await import('./widgets/checkout-flow.js');
    return renderCheckout(container, data, ctx);
  },
  accessibility: { role: 'form', label: 'Checkout' },
  estimatedHeight: 500,
});
```

While the async renderer loads, the registry displays a skeleton placeholder sized according to `estimatedHeight`.

See [CHAT_SDK_TECHNICAL_SPEC.md §4](../../CHAT_SDK_TECHNICAL_SPEC.md#4-widget-registry-specification) for full interface definitions.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Built-in widget types in production use | 10+ (of 12 shipped) | Widget render telemetry |
| Custom widget registrations | 50+ in production across all deployments | Registry telemetry |
| Widget render success rate | >99.5% (renders without error) | Error telemetry |
| P50 widget render latency (cached module) | <100ms | Performance marks |
| P95 widget render latency (lazy loaded) | <300ms | Performance marks |
| Widgets with complete accessibility metadata | 100% of built-in, >80% of custom | Registry validation telemetry |

### Success Criteria

1. A developer can create and register a custom widget (e.g., a flight booking card) in under 1 hour using the Widget SDK documentation.
2. A merchant can override a built-in widget (e.g., `product_details`) with a branded version by registering a widget with the same type name.
3. All 12 built-in widgets render correctly in 10+ languages and RTL layouts.
4. The registry validates accessibility metadata on registration and logs warnings for incomplete widgets.

---

## Critical User Journeys

### CUJ 1: Healthcare Appointment Scheduling
**Actor:** Developer at a telehealth company
**Goal:** Build a custom appointment scheduler widget that renders inside the chat

1. Developer reads Widget SDK docs
2. Defines JSON schema for appointment data (provider, available slots, location)
3. Implements render function with calendar UI using their existing component library
4. Registers widget with `chatSDK.registerWidget()`
5. Configures their GECX agent to emit `{ widget_type: 'appointment_scheduler', data: {...} }`
6. Widget renders inside the chat thread; user selects a slot; `ctx.emit('slot_selected', { ... })` sends the selection back to the agent

### CUJ 2: Merchant Overrides Product Display
**Actor:** Brand team at a luxury retailer
**Goal:** Replace the default product carousel with a branded, immersive product showcase

1. Brand team builds a custom `product_carousel` renderer with their design system
2. Registers it: `chatSDK.registerWidget({ type: 'product_carousel', ... })`
3. The custom registration overrides the built-in — all product carousels now render with the branded experience
4. The data schema is the same, so no agent changes are needed

### CUJ 3: Agent Declares Widget and User Interacts
**Actor:** End user shopping for furniture
**Goal:** Compare three sofas side by side and add one to cart

1. User: "Show me leather sofas under $2000"
2. Agent sends `{ widget_type: 'product_carousel', data: { products: [...] } }`
3. Registry looks up `product_carousel`, validates data, renders carousel
4. User swipes through products, taps "Compare" on three items
5. Agent sends `{ widget_type: 'product_comparison', data: { products: [...], attributes: [...] } }`
6. Comparison table renders with highlighted best values
7. User taps "Add to Cart" on the winning sofa → `ctx.emit('add_to_cart', { productId: '...' })`

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | `registerWidget()` accepts a WidgetDefinition with type, version, schema, render, and accessibility | P0 |
| FR-2 | `unregisterWidget()` removes a widget type from the registry | P0 |
| FR-3 | Registry validates incoming widget data against the JSON schema before rendering | P0 |
| FR-4 | Schema validation failures emit a `widget:error` event and render an error card | P0 |
| FR-5 | Widget render functions receive a sandboxed container, validated data, and WidgetContext | P0 |
| FR-6 | Render functions may return a cleanup function called on widget removal | P0 |
| FR-7 | Render functions may be async (return a Promise) for lazy loading | P0 |
| FR-8 | Async renders show a skeleton placeholder during loading | P0 |
| FR-9 | `estimatedHeight` is used to size the skeleton and minimize layout shift (CLS) | P1 |
| FR-10 | Registering a widget with an existing type name overwrites the previous registration | P0 |
| FR-11 | All 12 built-in widgets are registered using the public API (no internal shortcuts) | P0 |
| FR-12 | Registry supports a fallback renderer for unregistered types (error card in Phase 1, Generative UI in Phase 2) | P0 |
| FR-13 | `setFallback()` allows replacing the fallback renderer | P1 |
| FR-14 | Accessibility metadata is validated on registration; missing metadata produces a console warning | P0 |
| FR-15 | WidgetContext provides theme, locale, direction, viewport, emit(), t(), cspNonce | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Registry + built-in text/card widgets are <15 KB gzipped | P0 |
| NFR-2 | Individual widget renderers are <8 KB gzipped each | P0 |
| NFR-3 | Widget rendering is isolated — a throwing render function does not crash the SDK | P0 |
| NFR-4 | Widgets render correctly in LTR and RTL layouts | P0 |
| NFR-5 | Widgets respect the `prefers-reduced-motion` media query | P1 |
| NFR-6 | Widget containers enforce a maximum height with overflow scrolling to prevent layout abuse | P1 |

---

## Open Questions

1. **Should custom widgets render in the main DOM or in an iframe?** Iframes provide strict isolation but make theming and communication harder. Shadow DOM provides style isolation but not script isolation. Recommend: Shadow DOM by default, iframe sandbox as opt-in per widget.

2. **How do we version widgets?** If a widget is registered as v1.0.0 but the agent sends data intended for v2.0.0, the schema validation may fail. Need a versioning/negotiation strategy. Recommend: widget type includes version in registry, agent specifies minimum version, registry finds best match.

3. **Should we ship a Widget SDK (CLI tool, testing harness, preview tool)?** A developer toolkit would significantly improve the custom widget experience. Recommend: yes, but as a separate P1 deliverable within Phase 1.

4. **What's the maximum number of widgets per conversation?** Unbounded widget rendering could cause memory issues. Recommend: virtualize widgets outside the viewport, render only the last N + visible widgets.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Registry exposed via `chatSDK.registerWidget()`
- **Event Bus (PRD-002):** Widget interactions flow through the event bus
- **Accessibility Layer (PRD-005):** Widgets must conform to accessibility contracts
- **Streaming Renderer (PRD-004):** Widgets can appear mid-stream

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Registry API design review | April 2026 Week 1 | API surface + WidgetDefinition interface finalized |
| Registry implementation | April 2026 Week 3 | Registration, validation, rendering, fallback working |
| 6 built-in widgets shipped | May 2026 | Product carousel, details, comparison, order summary, quick actions, form |
| All 12 built-in widgets shipped | June 2026 | Full set including commerce widgets |
| Custom widget documentation + tutorial | June 2026 | "Build Your First Widget" guide published |
| GA with SDK v2 | July 2026 | Shipped as part of SDK v2 Core |
