# Chat SDK v2 — Product Requirements Documents

28 PRDs covering the complete Chat SDK v2 roadmap across three phases.

**Companion documents:**
- [Position Paper](../CHAT_SDK_VISION_2026.md) — "The Chat SDK is a Renderer, Not an App"
- [Technical Specification](../CHAT_SDK_TECHNICAL_SPEC.md) — Code-ready TypeScript interfaces
- [Roadmap](../CHAT_SDK_ROADMAP_2026_2027.md) — Phased delivery plan

---

## Phase 1: "Make It Real" (Q2-Q3 2026)

*Can a user discover, compare, and purchase a product entirely within the chat thread?*

### Core Platform + Trust (Q2)

| # | PRD | Priority | Description |
|---|-----|----------|-------------|
| 1 | [SDK v2 Core API](phase-1/01-sdk-v2-core-api.md) | P0 | Full lifecycle, messaging, context, session, event API |
| 2 | [Event Bus](phase-1/02-event-bus.md) | P0 | 30+ typed events, audit logging, analytics hooks |
| 3 | [Widget Registry](phase-1/03-widget-registry.md) | P0 | 12 built-in widgets + custom registration API |
| 4 | [Streaming Message Renderer](phase-1/04-streaming-message-renderer.md) | P0 | Token-by-token text + widget interleaving |
| 5 | [Accessibility Layer](phase-1/05-accessibility-layer.md) | P0 | WCAG 2.2 AA, keyboard nav, screen reader, VPAT |
| 6 | [Transaction Audit Trail](phase-1/06-transaction-audit-trail.md) | P0 | EU AI Act compliant immutable event log |
| 7 | [Iframe Sandbox Mode](phase-1/07-iframe-sandbox-mode.md) | P0 | Cross-origin isolation for enterprise security |
| 8 | [Mobile-First Responsive Design](phase-1/08-mobile-first-responsive-design.md) | P0 | Responsive layouts, touch optimization, performance |

### Commerce Foundation (Q3)

| # | PRD | Priority | Description |
|---|-----|----------|-------------|
| 9 | [UCP-Native Inline Checkout](phase-1/09-ucp-inline-checkout.md) | P0 | Cart, checkout flow, payment selection in-thread |
| 10 | [AP2 Consent Flows](phase-1/10-ap2-consent-flows.md) | P0 | Mandate rendering and cryptographic signing |
| 11 | [Embedded Checkout Bridge](phase-1/11-embedded-checkout-bridge.md) | P0 | JSON-RPC 2.0 bridge for merchant checkout |
| 12 | [Google Pay Integration](phase-1/12-google-pay-integration.md) | P0 | One-tap payment via Google Pay API |
| 13 | [Multilingual Rich Content](phase-1/13-multilingual-rich-content.md) | P0 | 10 languages, RTL layout, locale-aware formatting |
| 14 | [TypeScript + React SDKs](phase-1/14-typescript-react-sdk.md) | P1 | Type definitions, React components + hooks |
| 15 | [Conversation History API](phase-1/15-conversation-history-api.md) | P1 | Persistent, cross-session conversation storage |

---

## Phase 2: "Make It Intelligent" (Q4 2026)

*Can the SDK render anything an agent can imagine?*

| # | PRD | Priority | Description |
|---|-----|----------|-------------|
| 16 | [Generative UI Pipeline](phase-2/16-generative-ui-pipeline.md) | P0 | AI-rendered widgets for novel intents |
| 17 | [Multi-Agent Thread](phase-2/17-multi-agent-thread.md) | P0 | Agent identity, handoff UI, agent roster |
| 18 | [ACP Compatibility Layer](phase-2/18-acp-compatibility-layer.md) | P0 | Protocol-agnostic commerce (UCP + ACP) |
| 19 | [Cross-Merchant Cart](phase-2/19-cross-merchant-cart.md) | P0 | Unified cart spanning multiple retailers |
| 20 | [Proactive Engagement Engine](phase-2/20-proactive-engagement-engine.md) | P1 | Intent signals, smart triggers, cart recovery |
| 21 | [Image Understanding + Visual Search](phase-2/21-image-understanding-visual-search.md) | P1 | Camera capture, image-to-product search |
| 22 | [Voice-in-Chat](phase-2/22-voice-in-chat.md) | P1 | Inline voice messages with transcription |
| 23 | [Commerce Funnel Analytics](phase-2/23-commerce-funnel-analytics.md) | P1 | Conversion tracking, funnel visualization |
| 24 | [Plugin Architecture](phase-2/24-plugin-architecture.md) | P1 | Reusable extension packaging |
| 25 | [A2A + MCP Protocol Integration](phase-2/25-a2a-mcp-protocol-integration.md) | P1 | Multi-agent orchestration + tool connectivity |

---

## Phase 3: "Make It Scale" (Q1-Q2 2027)

*Can this be the default commerce surface for Google?*

| # | PRD | Priority | Description |
|---|-----|----------|-------------|
| 26 | [Native Mobile SDKs](phase-3/26-native-mobile-sdks.md) | P1 | iOS (Swift) + Android (Kotlin) SDKs |
| 27 | [BigQuery Analytics Export](phase-3/27-bigquery-analytics-export.md) | P1 | Streaming event export to BigQuery |
| 28 | [Real-Time Monitoring + Alerting](phase-3/28-realtime-monitoring-alerting.md) | P1 | Live dashboard, anomaly detection, alerts |

---

## PRD Template

Each PRD follows this structure:

1. **Introduction** — Problem statement and context
2. **What Are We Building** — Feature description with architecture details
3. **What Does Success Look Like** — Metrics and success criteria
4. **Critical User Journeys** — 2-3 detailed CUJs with step-by-step flows
5. **Requirements** — Functional and non-functional requirements with priority
6. **Open Questions** — Unresolved decisions with recommendations
7. **Dependencies** — Cross-PRD and external dependencies
8. **Milestones** — Delivery timeline with key dates

---

*Last updated: February 2026*
