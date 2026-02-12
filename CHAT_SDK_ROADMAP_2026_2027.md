# Chat SDK: One-Year Product Roadmap & Vision
## Gemini Enterprise for Customer Experience (GECX)
### FY2026-2027 | CONFIDENTIAL

---

> **"The conversation thread is becoming the universal commerce interface."**
>
> Every major technology company, payment network, and retailer has made significant production investments in this direction within the last 12 months. The Chat SDK is no longer a messaging widget — it is the front door to a multi-trillion-dollar platform shift.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Where We Are Today](#2-where-we-are-today)
3. [Market Context & Why Now](#3-market-context--why-now)
4. [Competitive Intelligence](#4-competitive-intelligence)
5. [Strategic Vision: The Chat SDK as Commerce Surface](#5-strategic-vision-the-chat-sdk-as-commerce-surface)
6. [The Five Strategic Pillars](#6-the-five-strategic-pillars)
7. [Phased Roadmap](#7-phased-roadmap)
8. [Feature Stack Rank](#8-feature-stack-rank)
9. [Key Bets & Risks](#9-key-bets--risks)
10. [Success Metrics](#10-success-metrics)
11. [Appendix: Research Sources](#11-appendix-research-sources)

---

## 1. Executive Summary

The GECX Chat SDK — externally marketed as the "chat widget" and internally as the Chat SDK — is the presentation layer through which every Shopping Agent, Food Ordering Agent, and customer service agent reaches end users. It is the single highest-leverage surface in the GECX stack: where platform capability meets customer experience, and where billions of dollars in agentic commerce will be transacted.

**Today, the SDK is thin.** Two JavaScript methods, four events, five pre-built widget types, and English-only rich content. It was built for an era of scripted chatbots, not agentic commerce.

**The market has moved.** ChatGPT processes 50M purchase-intent interactions daily. Amazon Rufus has driven $10B+ in incremental annualized sales. During Cyber Week 2025, AI agents influenced 20% of all orders ($67B GMV). McKinsey projects $3-5 trillion in agent-intermediated commerce by 2030.

**We have structural advantages no competitor can match.** Google owns the Shopping Graph, the broadest UCP coalition (20+ brands), the distribution surface (billions of daily searches, 650M+ Gemini users), and the only platform that unifies commerce and service in one agentic system.

**This roadmap transforms the Chat SDK from a messaging widget into Google's agentic commerce surface** — the place where agents discover, negotiate, transact, and resolve on behalf of users, powered by open protocols and rendered through generative, adaptive UI.

### The Roadmap at a Glance

| Phase | Timeline | Theme | Headline Capability |
|-------|----------|-------|-------------------|
| **Phase 1: Foundation** | Q2-Q3 2026 | "Unlock the Platform" | Extensible widget system, full SDK API, UCP-native checkout |
| **Phase 2: Differentiation** | Q3-Q4 2026 | "Commerce in Every Thread" | Generative UI, multi-agent orchestration, cross-merchant carts |
| **Phase 3: Dominance** | Q1-Q2 2027 | "The Agentic Surface" | Spatial computing, autonomous delegation, protocol-agnostic commerce |

---

## 2. Where We Are Today

### 2.1 Current SDK Capabilities

The Chat SDK (web widget) provides:

**Strengths:**
- Rapid deployment via CDN-hosted embed code — minimal engineering lift
- Deep visual theming — 40+ CSS design tokens following Material Design
- Multimodal modes — chat, voice, and mixed in a single component
- Five pre-built commerce widget types (Product Carousel, Product Details, Product Comparison, Order Summary, Quick Actions)
- Flexible auth — token broker, OAuth2, and custom API paths
- Built-in human agent handoff

**Critical Gaps:**

| Gap | Impact |
|-----|--------|
| **2 JavaScript methods** (`renderCustomText`, `renderCustomCard`) | Cannot programmatically control the widget, inject context, or build host-page integrations |
| **4 events** (loaded, close, error, cart-count) | No message-level events, no conversation lifecycle, no analytics hooks |
| **5 fixed widget types, no extensibility** | Any use case beyond e-commerce (healthcare, finance, scheduling) is blocked |
| **English-only rich content** | Hard blocker for global deployment |
| **No conversation history API** | Every interaction is ephemeral; no cross-session continuity |
| **No analytics/telemetry** | Zero observability into conversation quality, commerce conversion, or agent performance |
| **Shadow DOM only (no iframe sandbox)** | Documentation warns of XSS risks; shared localStorage with host page |
| **No programmatic open/close/minimize** | Cannot build proactive engagement, deep-linking, or context-aware triggers |
| **No multi-widget support** | Cannot deploy multiple agents on a single page |
| **No offline/reconnection handling** | No message queuing or graceful degradation |

### 2.2 Where the SDK Sits in the GECX Stack

```
┌─────────────────────────────────────────────────────────────┐
│  End-User Touchpoints                                       │
│  Web │ Mobile │ Voice │ Email │ Social │ Kiosks │ In-Car    │
├─────────────────────────────────────────────────────────────┤
│  ★ CHAT SDK / Web Widget / Omnichannel Gateway ★           │  ◄── YOU ARE HERE
├─────────────────────────────────────────────────────────────┤
│  CX Agent Studio                                            │
│  (Low-code builder, 35 templates, evaluation, tracing)      │
├─────────────────────────────────────────────────────────────┤
│  Conversational Agents Runtime (Dialogflow CX engine)       │
│  (Playbooks, flows, data stores, generative AI)             │
├─────────────────────────────────────────────────────────────┤
│  Gemini Models + Vertex AI                                  │
├─────────────────────────────────────────────────────────────┤
│  Google Cloud Infrastructure                                │
│  (BigQuery, Firestore, Pub/Sub, Cloud Storage)              │
└─────────────────────────────────────────────────────────────┘
```

**Strategic implication:** The SDK is the customer-facing front door to the entire GECX platform. Every agent — shopping, food ordering, customer service — must render through this surface. As GECX expands transactional capabilities, the SDK must evolve from a conversation widget into a full commerce and service interface.

---

## 3. Market Context & Why Now

### 3.1 The Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Agent-intermediated commerce (2030 projection) | $3-5T consumer + $15T B2B | McKinsey |
| AI agents market (2025 → 2034) | $7.6B → $236B | Precedence Research |
| Agentic AI in retail (2030) | $175.1B | Industry analysis |
| AI-influenced orders, Cyber Week 2025 | 20% of all orders (~$67B GMV) | Adobe/Salesforce |
| AI-driven traffic to retail sites, Black Friday 2025 | +805% YoY | Adobe |
| ChatGPT daily purchase-intent interactions | 50M | OpenAI estimates |
| Amazon Rufus users | 250M+ | Amazon |
| Consumers comfortable with AI shopping | 44% (59% ages 18-34) | Consumer surveys |
| Voice commerce market (2034) | $714.5B | WildNet Edge |
| Retailers with AI agents: sales growth premium | +32% vs. competitors | Industry analysis |

### 3.2 The Protocol Stack Is Crystallizing

For the first time, a coherent open protocol architecture for agentic commerce is emerging:

```
LAYER 4 — COMMERCE:        UCP (Google/Shopify) + ACP (OpenAI/Stripe)
LAYER 3 — AGENT-TO-AGENT:  A2A Protocol (Google, 50+ partners)
LAYER 2 — AGENT-TO-TOOLS:  MCP (Anthropic/AAIF, 97M+ monthly SDK downloads)
LAYER 1 — IDENTITY/TRUST:  KYA + Visa TAP + Mastercard Agent Pay + AP2
FOUNDATION — GOVERNANCE:    Agentic AI Foundation (Linux Foundation)
```

**Google authored or co-authored three of these five layers** (UCP, A2A, AP2). The Chat SDK must be the reference implementation surface for these protocols — the place where they come to life for end users.

### 3.3 The Chat UI Is Being Reinvented

Static message bubbles are giving way to **Generative UI** — dynamically rendered, context-aware interfaces assembled by the AI model in real time:

- Google Research demonstrated Gemini 3 Pro creating entire interactive experiences (tables, maps, visuals) tailored to specific requests
- MCP Apps (SEP-1865) introduces standardized interactive UIs via a `ui://` URI scheme
- Six major frameworks competing: MCP Apps, AG-UI (Oracle), AI SDK 6 (Vercel), ChatKit (OpenAI), Flutter GenUI SDK (Google), Thesys
- 3D/AR product visualization in chat shows up to **11x higher conversion** vs. flat images

**The Chat SDK should set the standard here, not follow it.**

---

## 4. Competitive Intelligence

### 4.1 Shopping Agent Landscape

| Player | Scale | Checkout | Protocol | Key Strength | Key Weakness |
|--------|-------|----------|----------|-------------|-------------|
| **Amazon Rufus** | 250M+ users | Native (Amazon only) | None (walled garden) | $10B+ incremental sales, account memory | Amazon-only catalog |
| **ChatGPT Shopping** | 50M purchase-intent/day | Instant Checkout (Stripe/ACP) | ACP (open source) | End-to-end research-to-buy | EU/UK restrictions, merchant fees |
| **Perplexity** | 780M queries/mo | PayPal Instant Buy | None | Free, research-native | Small catalog, Amazon lawsuit |
| **Klarna** | 1.3M CS chats/mo | Klarna BNPL | APP (open) | 100M+ products discoverable | Quality issues, BNPL perception |
| **Google (us)** | Billions of searches | UCP + AP2 | UCP (open source) | Shopping Graph, broadest coalition | Late to conversational shopping |
| **Microsoft Copilot** | M365 user base | Copilot Checkout | None | Enterprise integration | Early stage commerce |
| **Meta** | 3B+ social users | Early stage | None | Social graph, creator commerce | Immature |

**Our gap:** We have the best infrastructure (Shopping Graph, UCP, AP2, Gemini) but the thinnest front-end surface. ChatGPT and Perplexity deliver richer in-chat commerce experiences today than our Chat SDK can support. **The SDK is the bottleneck.**

### 4.2 Enterprise Chat SDK Landscape

| Player | Base Price | AI Pricing | Resolution Rate | Deploy Speed | Best For |
|--------|-----------|------------|----------------|-------------|---------|
| **Salesforce Agentforce** | $125/user/mo | $2/conversation | 70% (best case) | Weeks-months | Large enterprise CRM |
| **Microsoft Dynamics** | $50/user/mo | Included in tiers | Not disclosed | Weeks-months | Microsoft ecosystem |
| **Zendesk** | $55/agent/mo | $1.50-$2/AR | 25-40% | Days-weeks | Mid-market helpdesk |
| **Intercom Fin** | $29/seat/mo | $0.99/resolution | 60% (claimed) | Under 1 hour | Startups/SMBs |
| **Freshworks** | $15/agent/mo | $0.50/interaction | 80% (claimed) | Minutes (claimed) | Budget-conscious |
| **Twilio Flex** | $1/hour | $0.035/voice min | N/A (DIY) | 2+ weeks | Engineering-led orgs |
| **Google GECX** | Contact sales | Per-session | Not disclosed | Days (35 templates) | Retail + commerce |

**Our differentiator:** We are the only platform that unifies shopping and service agents in one system with shared conversational context. No competitor collapses the commerce/service boundary.

### 4.3 The Protocol Wars

| Protocol | Sponsor | Scope | Status |
|----------|---------|-------|--------|
| **UCP** | Google + Shopify + 20 brands | Full commerce lifecycle | Launched Jan 2026 |
| **ACP** | OpenAI + Stripe | Checkout/payments | Launched Sep 2025 |
| **APP** | Klarna | Product discovery | Launched Dec 2025 |
| **TAP** | Visa + Cloudflare | Identity/trust for payments | Launched Oct 2025 |
| **AP2** | Google + partners | Payment authorization | Launched Jan 2026 |

**Strategic reality:** Winning merchants will implement multiple protocols. The Chat SDK must be **protocol-agnostic at the UI layer** — rendering commerce flows regardless of which protocol the backend uses.

---

## 5. Strategic Vision: The Chat SDK as Commerce Surface

### The One-Sentence Vision

**The Chat SDK becomes the world's most capable agentic commerce surface — where AI agents discover, negotiate, transact, and resolve on behalf of users through generative, adaptive UI powered by open protocols.**

### What This Means Concretely

The Chat SDK transforms from:

| From (Today) | To (2027) |
|--------------|-----------|
| Static message bubbles with 5 fixed widget types | Generative UI with unlimited composable components |
| 2 JS methods, 4 events | Full programmatic API with 50+ methods, rich event system, plugin architecture |
| English-only rich content | 40+ language support for all content types |
| Ephemeral conversations | Persistent, cross-session, cross-device conversation history |
| Single-agent, single-merchant | Multi-agent orchestration, cross-merchant commerce |
| Chat-only | True multimodal: voice, text, image, video, 3D/AR in one thread |
| Passive widget waiting for clicks | Proactive engagement engine with intent-aware triggers |
| Web-only embed | Web, mobile SDK, spatial computing, kiosk, in-car |
| No commerce primitives | Full UCP/ACP-native checkout, cart management, payment flows |
| Zero observability | Real-time analytics, conversion tracking, agent performance dashboards |

### The Killer Product Concept: "Commerce Threads"

We introduce the concept of **Commerce Threads** — persistent, context-rich conversation spaces where:

1. **Every thread has memory.** Cross-session history, user preferences, purchase history, loyalty status — all available to every agent in the thread.
2. **Agents compose the UI.** Instead of choosing from 5 widget types, agents declare UI intent and the SDK renders the optimal interface — a product comparison table, a checkout flow, an AR try-on, a delivery scheduler — using a generative UI pipeline.
3. **Multiple agents collaborate.** A discovery agent finds products, a comparison agent evaluates them, a checkout agent completes the purchase, and a service agent handles post-purchase — all in one thread with seamless handoffs.
4. **Merchants bring their experience.** Via UCP's Embedded Checkout Protocol, merchants can inject branded checkout experiences into the thread without breaking the conversation flow.
5. **Users stay in control.** AP2 Mandates provide cryptographic proof of user intent at every transaction step. Users see exactly what they're authorizing, can set budgets, and can revoke delegation at any time.

This is not a chatbot. This is the **post-browser commerce experience**.

---

## 6. The Five Strategic Pillars

### Pillar 1: Extensible Widget Architecture
*"From 5 fixed widgets to unlimited composable components"*

**The Problem:** The SDK's 5 pre-built widget types (Product Carousel, Product Details, Product Comparison, Order Summary, Quick Actions) cover basic e-commerce but block every other vertical — healthcare forms, financial calculators, appointment scheduling, document collection, insurance quotes, travel booking.

**The Solution: Widget Registry + Generative UI Pipeline**

```
┌─────────────────────────────────────────────┐
│  Agent declares UI intent (structured JSON)  │
├─────────────────────────────────────────────┤
│  Widget Registry resolves to component       │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ Built-in│ │ Merchant │ │ Generative   │ │
│  │ Widgets │ │ Custom   │ │ (AI-rendered)│ │
│  └─────────┘ └──────────┘ └──────────────┘ │
├─────────────────────────────────────────────┤
│  Sandboxed Renderer (iframe isolation)       │
├─────────────────────────────────────────────┤
│  Chat Thread                                 │
└─────────────────────────────────────────────┘
```

**Key deliverables:**
- **Widget Registry API** — register custom widget types with schemas, renderers, and interaction handlers
- **Widget SDK** — developer toolkit for building custom widgets with TypeScript types, testing harness, and preview tools
- **15+ new built-in widgets** — form, calendar/scheduler, map/location, payment, file upload/document, chart/data visualization, rating/review, progress tracker, address input, signature capture, video player, countdown timer, loyalty card, subscription manager, split-view comparison
- **Generative Widget Renderer** — for cases where no registered widget matches, the SDK uses Gemini to generate appropriate UI dynamically within a sandboxed iframe
- **Merchant Widget Injection** — via UCP's Embedded Checkout Protocol, merchants inject branded components using JSON-RPC 2.0 bi-directional messaging
- **Multilingual widget content** — all widgets render in the user's language, not just English

### Pillar 2: Protocol-Native Commerce
*"UCP and AP2 come to life in the chat thread"*

**The Problem:** The SDK has a `df-update-cart-count` event and an Order Summary widget, but no actual commerce primitives. It cannot render a checkout flow, handle payment selection, manage fulfillment options, or process UCP's three-state checkout model (`incomplete` → `requires_escalation` → `ready_for_complete`).

**The Solution: Commerce Thread Engine**

The SDK natively implements UCP checkout flows as first-class conversation elements:

**Key deliverables:**
- **Inline Cart Widget** — real-time cart management (add/remove/modify) within the conversation thread, with UCP line item sync
- **Checkout Flow Component** — multi-step checkout rendered inline: shipping → payment → confirmation, adapting to UCP's state machine
- **Payment Method Selector** — renders available payment handlers from UCP capability negotiation; integrates with Google Pay, AP2 mandates
- **Fulfillment Picker** — shipping, pickup, local delivery, delivery windows — driven by UCP fulfillment extensions
- **Discount & Loyalty Widget** — apply promo codes, enroll in loyalty programs, redeem points — driven by UCP discount and loyalty extensions
- **Embedded Checkout Bridge** — when UCP returns `requires_escalation`, the SDK seamlessly renders the merchant's embedded checkout (iframe + JSON-RPC 2.0) and returns the user to the conversation after completion
- **Cross-Merchant Cart** — build a unified cart spanning multiple merchants (a discovery agent comparing products from three retailers), with per-merchant checkout handled independently
- **AP2 Consent Flow** — present Intent Mandates, Checkout Mandates, and Payment Mandates as clear, signable consent cards within the thread
- **ACP Compatibility Layer** — render checkout flows from ACP-powered merchants (Stripe/OpenAI ecosystem) alongside UCP flows, making the SDK protocol-agnostic at the presentation layer
- **Order Tracking Widget** — post-purchase order status, shipping tracking, and return initiation within the same thread

### Pillar 3: Full Developer Platform
*"From 2 methods to a complete SDK"*

**The Problem:** `renderCustomText()` and `renderCustomCard()` are insufficient for any integration beyond "embed and forget." Developers cannot programmatically control the widget, listen to conversation events, inject context, manage sessions, or build analytics.

**The Solution: Chat SDK v2 — Full Programmatic API**

**Core API Surface:**

```typescript
// Lifecycle
chatSDK.open()
chatSDK.close()
chatSDK.minimize()
chatSDK.destroy()
chatSDK.reset()

// Messaging
chatSDK.sendMessage(text: string, metadata?: object)
chatSDK.sendAction(actionId: string, payload: object)
chatSDK.renderWidget(widgetType: string, data: object)

// Context
chatSDK.setContext(key: string, value: any)
chatSDK.getContext(key: string): any
chatSDK.setUserIdentity(identity: UserIdentity)
chatSDK.setLanguage(languageCode: string)

// Session
chatSDK.getSessionId(): string
chatSDK.getConversationHistory(): Message[]
chatSDK.restoreSession(sessionId: string)
chatSDK.clearHistory()

// Commerce
chatSDK.getCart(): CartState
chatSDK.updateCart(changes: CartUpdate)
chatSDK.initiateCheckout(options?: CheckoutOptions)

// Events (30+ event types)
chatSDK.on('message:sent', handler)
chatSDK.on('message:received', handler)
chatSDK.on('widget:interaction', handler)
chatSDK.on('agent:handoff', handler)
chatSDK.on('commerce:cart-updated', handler)
chatSDK.on('commerce:checkout-started', handler)
chatSDK.on('commerce:payment-completed', handler)
chatSDK.on('commerce:order-confirmed', handler)
chatSDK.on('session:started', handler)
chatSDK.on('session:restored', handler)
chatSDK.on('session:ended', handler)
chatSDK.on('typing:start', handler)
chatSDK.on('typing:stop', handler)
chatSDK.on('error', handler)
chatSDK.on('proactive:triggered', handler)
// ... and more

// Plugin System
chatSDK.registerPlugin(plugin: ChatPlugin)
chatSDK.registerWidget(widgetType: string, renderer: WidgetRenderer)

// Analytics
chatSDK.getAnalytics(): AnalyticsSnapshot
chatSDK.trackEvent(name: string, properties: object)
```

**Key deliverables:**
- **Chat SDK v2 JavaScript API** — full lifecycle, messaging, context, session, commerce, and analytics methods
- **TypeScript SDK** — fully typed with IntelliSense support
- **React SDK** — `<ChatProvider>`, `<ChatWidget>`, `<ChatTrigger>` components with hooks (`useChatSDK`, `useConversation`, `useCommerce`)
- **Web Components SDK** — framework-agnostic custom elements with Shadow DOM isolation
- **Plugin Architecture** — register custom plugins that intercept events, modify rendering, and extend functionality
- **Developer Console** — debug panel for inspecting conversation state, widget renders, commerce flows, and API calls in real time
- **Webhook Gateway** — server-side event delivery for conversation events, commerce transactions, and agent handoffs
- **Conversation History API** — persistent, queryable, cross-session history with server-side storage (Firestore-backed)
- **Documentation Site** — comprehensive guides, API reference, interactive playground, and migration guide from v1

### Pillar 4: Multimodal & Multi-Agent
*"Voice, text, image, and video in one thread — with multiple agents collaborating"*

**The Problem:** The current SDK supports text and optional voice input, but treats them as separate modalities. There is no support for image-in-chat, video, or AR. There is no concept of multiple agents within a single conversation.

**The Solution: Unified Multimodal Thread + Agent Orchestration**

**Key deliverables:**
- **Multimodal Message Bus** — voice, text, images, video, and rich media as equal first-class message types within a single unified thread
- **Voice-in-Chat** — inline voice messages with automatic transcription and agent response in user's preferred modality (voice or text)
- **Image Understanding** — users share product photos, screenshots, or documents; the agent processes them inline (powered by Gemini's multimodal capabilities)
- **Visual Search Widget** — "find products like this" from a user-uploaded photo, rendered as a product carousel
- **3D/AR Product Viewer** — inline 3D product models with AR try-on via WebXR, compatible with visionOS and mobile AR
- **Multi-Agent Thread** — conversation threads where multiple specialized agents participate, with visible agent identity and smooth context-preserving handoffs
- **Agent Roster** — UI showing which agents are available or active in the thread (e.g., "Shopping Assistant" hands off to "Returns Specialist")
- **A2A Protocol Integration** — multi-agent orchestration using Google's Agent-to-Agent protocol for agent discovery, capability negotiation, and task delegation
- **Collaborative Shopping** — shared threads where multiple users (e.g., a couple planning a purchase) interact with the same agent simultaneously

### Pillar 5: Proactive Intelligence & Trust
*"The SDK that knows when to speak up — and earns the right to transact"*

**The Problem:** The SDK is entirely reactive — it waits for the user to click the chat bubble. There are no proactive engagement patterns, no trust verification for agentic transactions, and no analytics to optimize the experience.

**The Solution: Engagement Engine + Trust Layer + Analytics Platform**

**Key deliverables:**

**Proactive Engagement:**
- **Intent Signal Engine** — detect user behavior signals (time on page, scroll depth, cart abandonment, error encounters) and trigger contextual proactive messages
- **Smart Triggers API** — configure rule-based and ML-driven triggers: "If user views product page > 30s and hasn't added to cart, offer size guidance"
- **Notification Widget** — subtle, non-intrusive notification badge on the chat bubble with context-specific prompts
- **Proactive Commerce Nudges** — "The item in your cart is now 20% off" / "Your subscription renews in 3 days — want to review?"
- **Exit-Intent Interception** — detect navigation away and offer relevant assistance

**Trust & Security:**
- **AP2 Mandate Renderer** — clear, human-readable consent cards for Intent, Checkout, and Payment mandates with cryptographic signing
- **Agent Identity Verification** — display verified agent identity badges, authority chains, and trust scores per the emerging KYA (Know Your Agent) framework
- **Transaction Audit Trail** — complete, immutable log of every agent action, user consent, and transaction for compliance (EU AI Act enforceable August 2026)
- **Iframe Sandbox Mode** — optional strict iframe isolation for enterprise deployments handling sensitive data, replacing the current Shadow DOM-only approach
- **Data Isolation** — isolated storage model (no shared localStorage with host page), encrypted session state
- **Content Security Policy** — enforced CSP headers for all widget content, XSS mitigation built into the rendering pipeline

**Analytics & Observability:**
- **Conversation Analytics Dashboard** — message volume, response times, resolution rates, CSAT, conversation flow visualization
- **Commerce Funnel Analytics** — product views → cart adds → checkout starts → payment → confirmation, with drop-off analysis
- **Widget Interaction Heatmaps** — which widgets get the most engagement, which are abandoned
- **Agent Performance Metrics** — per-agent resolution rates, escalation rates, average handling time
- **Real-Time Monitoring** — live conversation feed with anomaly detection and alerting
- **BigQuery Export** — raw event streaming to BigQuery for custom analysis and ML model training
- **A/B Testing Framework** — test different widget layouts, proactive triggers, and agent behaviors with statistical significance tracking

---

## 7. Phased Roadmap

### Phase 1: Foundation — "Unlock the Platform"
**Q2-Q3 2026 (April - September)**

The goal of Phase 1 is to close the critical gaps that make the SDK a bottleneck and lay the technical foundation for everything that follows.

#### Q2 2026 (April - June): Core Platform

| # | Feature | Pillar | Priority | Rationale |
|---|---------|--------|----------|-----------|
| 1 | **Chat SDK v2 JavaScript API** — full lifecycle, messaging, context, and session methods | Developer Platform | P0 | Unblocks all host-page integrations; required for everything else |
| 2 | **Widget Registry + 10 new built-in widgets** | Extensible Widgets | P0 | Unblocks vertical expansion beyond e-commerce |
| 3 | **Multilingual rich content** (top 10 languages) | Extensible Widgets | P0 | Hard blocker for global customers (Woolworths AU, Zalando EU) |
| 4 | **30+ events** (message lifecycle, conversation lifecycle, commerce, typing) | Developer Platform | P0 | Enables analytics, integrations, and custom workflows |
| 5 | **Conversation History API** with Firestore persistence | Developer Platform | P0 | Cross-session continuity; required for Commerce Threads |
| 6 | **Iframe Sandbox Mode** | Trust | P0 | Enterprise security requirement; addresses documented XSS warnings |
| 7 | **TypeScript SDK + React SDK** | Developer Platform | P1 | Developer experience; captures React-dominant frontend ecosystem |
| 8 | **Developer Console** (debug panel) | Developer Platform | P1 | Reduces integration friction; accelerates developer adoption |

#### Q3 2026 (July - September): Commerce Foundation

| # | Feature | Pillar | Priority | Rationale |
|---|---------|--------|----------|-----------|
| 9 | **UCP-Native Inline Checkout** — cart widget, checkout flow, payment selector | Protocol Commerce | P0 | Core differentiator; makes UCP real for end users |
| 10 | **AP2 Consent Flow** — mandate rendering and signing | Trust | P0 | Required for any UCP transaction; EU AI Act prep |
| 11 | **Embedded Checkout Bridge** (UCP `requires_escalation` handling) | Protocol Commerce | P0 | Handles the hybrid agent/human checkout flow UCP requires |
| 12 | **Google Pay Integration** in checkout flow | Protocol Commerce | P0 | Default payment path for UCP; drives Google Pay adoption |
| 13 | **Fulfillment Picker** (shipping, pickup, delivery windows) | Protocol Commerce | P1 | Key merchant requirement; driven by UCP fulfillment extensions |
| 14 | **Discount & Loyalty Widget** | Protocol Commerce | P1 | Revenue driver for merchants; UCP discount/loyalty extensions |
| 15 | **Basic Analytics Dashboard** — conversation volume, commerce events, error rates | Analytics | P1 | Minimum viable observability |
| 16 | **Webhook Gateway** for server-side event delivery | Developer Platform | P1 | Enables server-side integrations, CRM sync, alerting |

**Phase 1 Exit Criteria:**
- SDK v2 API is GA with full documentation
- UCP checkout flow works end-to-end in the chat thread
- At least 2 launch partners (e.g., Kroger, Lowe's) live with new SDK
- Widget Registry supports custom widget registration
- Rich content renders in 10+ languages

---

### Phase 2: Differentiation — "Commerce in Every Thread"
**Q3-Q4 2026 (October - December)**

Phase 2 introduces the capabilities that make the Chat SDK categorically different from any competitor's chat experience.

#### Q4 2026 (October - December): Generative + Multi-Agent

| # | Feature | Pillar | Priority | Rationale |
|---|---------|--------|----------|-----------|
| 17 | **Generative UI Pipeline** — AI-rendered widgets for uncovered intents | Extensible Widgets | P0 | Eliminates widget coverage gaps; enables infinite use cases |
| 18 | **Multi-Agent Thread** with agent identity and handoff UI | Multi-Agent | P0 | Key GECX differentiator (shopping → service in one thread) |
| 19 | **Cross-Merchant Cart** — unified cart spanning multiple retailers | Protocol Commerce | P0 | Comparison shopping killer feature; leverages Shopping Graph |
| 20 | **ACP Compatibility Layer** — render OpenAI/Stripe merchant checkouts | Protocol Commerce | P0 | Protocol-agnostic surface; captures merchants on both UCP and ACP |
| 21 | **Voice-in-Chat** — inline voice messages with transcription | Multimodal | P1 | Matches Salesforce Agentforce Voice and Shopify Sidekick voice |
| 22 | **Image Understanding** — visual search from user photos | Multimodal | P1 | Gemini multimodal advantage; high conversion impact |
| 23 | **Proactive Engagement Engine** — intent signals + smart triggers | Proactive | P1 | Shifts from reactive to anticipatory; major competitor gap |
| 24 | **Plugin Architecture** — third-party plugin registry | Developer Platform | P1 | Enables ecosystem; Shopify/Salesforce connector plugins |
| 25 | **Commerce Funnel Analytics** — full conversion tracking | Analytics | P1 | Required for merchant ROI measurement |
| 26 | **A2A Protocol Integration** for multi-agent orchestration | Multi-Agent | P1 | Connects to Google's A2A ecosystem |
| 27 | **Agent Identity Verification** + KYA framework | Trust | P1 | Differentiator for enterprise trust; EU AI Act compliance |
| 28 | **A/B Testing Framework** | Analytics | P2 | Enables data-driven optimization of chat experiences |
| 29 | **Order Tracking & Returns Widget** | Protocol Commerce | P1 | Post-purchase lifecycle in the same thread |
| 30 | **Mobile Web Optimization** — responsive, touch-native experience | Platform | P1 | Mobile is 60%+ of e-commerce traffic |

**Phase 2 Exit Criteria:**
- Generative UI renders custom widgets from agent intent with <500ms latency
- Multi-agent handoff works between shopping and service agents in one thread
- Cross-merchant cart aggregates products from 3+ retailers
- ACP checkout renders alongside UCP checkout in same thread
- 5+ launch partners live; 2+ using proactive engagement

---

### Phase 3: Dominance — "The Agentic Surface"
**Q1-Q2 2027 (January - June)**

Phase 3 pushes into forward-looking capabilities that establish the Chat SDK as the definitive agentic commerce surface.

#### Q1 2027 (January - March): Spatial + Autonomous

| # | Feature | Pillar | Priority | Rationale |
|---|---------|--------|----------|-----------|
| 31 | **3D/AR Product Viewer** — WebXR inline viewer with AR try-on | Multimodal | P1 | 11x conversion lift; Apple visionOS 26 compatible |
| 32 | **Autonomous Delegation Mode** — user sets budget/rules, agent shops independently | Proactive | P1 | Amazon Rufus auto-buy competitor; highest-value power users |
| 33 | **Collaborative Shopping** — shared threads with multiple users | Multi-Agent | P1 | Social commerce; differentiator vs. single-user competitors |
| 34 | **Native Mobile SDKs** (iOS + Android) | Platform | P1 | Break out of web-only; app integration for Kroger, Papa Johns |
| 35 | **BigQuery Export + Streaming** | Analytics | P1 | Enterprise analytics; feeds into existing BI infrastructure |
| 36 | **Transaction Audit Trail** | Trust | P0 | EU AI Act compliance (enforceable August 2026); enterprise requirement |

#### Q2 2027 (April - June): Ecosystem + Scale

| # | Feature | Pillar | Priority | Rationale |
|---|---------|--------|----------|-----------|
| 37 | **Spatial Computing Surface** — visionOS, WebXR immersive thread | Multimodal | P2 | Forward bet; positions for spatial commerce era |
| 38 | **Subscription Management Widget** — renewals, billing, cross-vendor optimization | Protocol Commerce | P1 | High-retention use case; recurring revenue for merchants |
| 39 | **B2B Procurement Workflows** — RFQ, bid comparison, contract negotiation | Protocol Commerce | P2 | Taps into $15T B2B opportunity |
| 40 | **Widget Marketplace** — third-party widget discovery and installation | Extensible Widgets | P2 | Ecosystem flywheel; developer community |
| 41 | **Cross-Border Commerce** — multi-currency, international fulfillment | Protocol Commerce | P2 | Global expansion; UCP multi-market support |
| 42 | **Kiosk & In-Car SDK** — embedded surface for physical commerce | Platform | P2 | Papa Johns, automotive partnerships; IoT touchpoints |
| 43 | **Real-Time Monitoring + Anomaly Detection** | Analytics | P1 | Enterprise-grade operational reliability |
| 44 | **MCP Integration** for agent-to-tool connectivity | Multi-Agent | P1 | Protocol completeness; connects to Anthropic/AAIF ecosystem |

**Phase 3 Exit Criteria:**
- 3D/AR viewer deployed with at least one furniture/fashion retailer
- Autonomous delegation mode live with spending limits and approval flows
- Native iOS and Android SDKs in beta
- EU AI Act compliance verified for transaction audit trail
- 20+ partners live on Chat SDK v2

---

## 8. Feature Stack Rank

### Tier 1: Must-Ship (P0) — Blocks revenue or creates unacceptable risk

| Rank | Feature | Phase | Rationale |
|------|---------|-------|-----------|
| 1 | Chat SDK v2 JavaScript API | Phase 1 | Everything depends on this |
| 2 | Widget Registry + new built-in widgets | Phase 1 | Vertical expansion blocked without this |
| 3 | UCP-Native Inline Checkout | Phase 1 | Core value prop; makes UCP real for users |
| 4 | AP2 Consent Flow | Phase 1 | Required for any UCP transaction |
| 5 | Multilingual rich content | Phase 1 | Global customer blocker |
| 6 | 30+ events system | Phase 1 | Analytics and integrations require this |
| 7 | Conversation History API | Phase 1 | Cross-session continuity is table stakes |
| 8 | Iframe Sandbox Mode | Phase 1 | Enterprise security requirement |
| 9 | Embedded Checkout Bridge | Phase 1 | UCP `requires_escalation` handling |
| 10 | Google Pay integration | Phase 1 | Default payment path |
| 11 | Generative UI Pipeline | Phase 2 | Eliminates widget coverage ceiling |
| 12 | Multi-Agent Thread | Phase 2 | GECX's key differentiator |
| 13 | Cross-Merchant Cart | Phase 2 | Shopping Graph monetization |
| 14 | ACP Compatibility Layer | Phase 2 | Protocol-agnostic positioning |
| 15 | Transaction Audit Trail | Phase 3 | EU AI Act compliance (Aug 2026 deadline) |

### Tier 2: Should-Ship (P1) — Strong competitive or customer value

| Rank | Feature | Phase |
|------|---------|-------|
| 16 | TypeScript SDK + React SDK | Phase 1 |
| 17 | Developer Console | Phase 1 |
| 18 | Fulfillment Picker | Phase 1 |
| 19 | Discount & Loyalty Widget | Phase 1 |
| 20 | Basic Analytics Dashboard | Phase 1 |
| 21 | Webhook Gateway | Phase 1 |
| 22 | Voice-in-Chat | Phase 2 |
| 23 | Image Understanding | Phase 2 |
| 24 | Proactive Engagement Engine | Phase 2 |
| 25 | Plugin Architecture | Phase 2 |
| 26 | Commerce Funnel Analytics | Phase 2 |
| 27 | A2A Protocol Integration | Phase 2 |
| 28 | Agent Identity Verification | Phase 2 |
| 29 | Order Tracking & Returns | Phase 2 |
| 30 | Mobile Web Optimization | Phase 2 |
| 31 | 3D/AR Product Viewer | Phase 3 |
| 32 | Autonomous Delegation Mode | Phase 3 |
| 33 | Collaborative Shopping | Phase 3 |
| 34 | Native Mobile SDKs | Phase 3 |
| 35 | BigQuery Export | Phase 3 |
| 36 | Subscription Management | Phase 3 |
| 37 | MCP Integration | Phase 3 |
| 38 | Real-Time Monitoring | Phase 3 |

### Tier 3: Could-Ship (P2) — Forward bets and ecosystem plays

| Rank | Feature | Phase |
|------|---------|-------|
| 39 | A/B Testing Framework | Phase 2 |
| 40 | Spatial Computing Surface | Phase 3 |
| 41 | B2B Procurement Workflows | Phase 3 |
| 42 | Widget Marketplace | Phase 3 |
| 43 | Cross-Border Commerce | Phase 3 |
| 44 | Kiosk & In-Car SDK | Phase 3 |

---

## 9. Key Bets & Risks

### Bets We're Making

| Bet | Thesis | Validation Signal |
|-----|--------|-------------------|
| **Generative UI is the future of chat** | Static widget types will be replaced by AI-composed interfaces within 2 years | Google Research demo; MCP Apps spec; 6 competing frameworks |
| **UCP wins the protocol war** | Broadest coalition + Google distribution + Shopify merchant base = dominant standard | 20+ brands signed; Shopify/Walmart/Target committed; decentralized discovery model |
| **Commerce and service converge** | The line between "helping someone buy" and "helping after they buy" dissolves | GECX architecture; Amazon Rufus covers both; industry consensus |
| **Multi-agent is the architecture** | Single-agent systems will be replaced by orchestrated specialist agents | 80% of enterprises planning multi-agent; A2A protocol adoption |
| **Trust infrastructure is the sleeper moat** | Whoever solves agent identity, consent, and audit wins enterprise | EU AI Act; Visa TAP; 180% fraud increase; AP2 mandates |

### Risks We're Managing

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Protocol fragmentation** — UCP, ACP, APP, TAP all competing | High | Build protocol-agnostic UI layer; support both UCP and ACP |
| **EU AI Act compliance** — enforceable August 2026 | High | Transaction audit trail in Phase 1-2; AP2 mandates provide traceability |
| **Enterprise trust deficit** — Google's product deprecation history | Medium | Maintain backward compatibility; clear migration paths; long-term support commitments |
| **Developer adoption** — SDK v2 is a breaking change | Medium | Migration tooling; parallel v1/v2 support during transition; comprehensive docs |
| **Generative UI latency** — AI-rendered widgets must be fast | Medium | Pre-compute common patterns; edge caching; fallback to registered widgets |
| **Multi-agent complexity** — Deloitte predicts 40%+ project cancellations | Medium | Provide opinionated defaults, testing harnesses, observability tools |
| **Security surface expansion** — more API = more attack vectors | High | Security review per feature; mandatory iframe sandbox for commerce; CSP enforcement |
| **Competitive response** — ChatGPT/Microsoft accelerating commerce features | High | Leverage unique GECX advantage (unified commerce+service); move fast on Phase 1 |

---

## 10. Success Metrics

### North Star Metric
**Commerce GMV transacted through the Chat SDK** — the total dollar value of transactions completed within the chat thread, across all merchants and protocols.

### Phase 1 Metrics (Q2-Q3 2026)

| Metric | Target | Measurement |
|--------|--------|-------------|
| SDK v2 API adoption | 50+ enterprise deployments | Deployment tracking |
| Widget types in production use | 15+ (including 5+ custom) | Widget Registry analytics |
| UCP checkout completion rate | >60% of initiated checkouts | Commerce funnel |
| Languages supported for rich content | 10+ | Configuration count |
| Developer NPS | >40 | Quarterly survey |
| P50 widget render latency | <200ms | Performance monitoring |
| Security incidents | 0 critical | Security monitoring |

### Phase 2 Metrics (Q3-Q4 2026)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Commerce GMV through SDK | $100M+ monthly | Transaction tracking |
| Multi-agent thread adoption | 30% of enterprise deployments | Feature analytics |
| Cross-merchant cart usage | 10K+ daily cross-merchant carts | Commerce analytics |
| Proactive engagement conversion | 15%+ engagement rate on triggers | A/B testing |
| Generative UI widget renders | 100K+ daily | Rendering analytics |
| ACP + UCP dual-protocol deployments | 10+ merchants | Deployment tracking |

### Phase 3 Metrics (Q1-Q2 2027)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Commerce GMV through SDK | $500M+ monthly | Transaction tracking |
| Total enterprise deployments | 200+ | Deployment tracking |
| 3D/AR engagement rate | 25%+ higher than 2D product cards | A/B testing |
| Autonomous delegation transactions | 50K+ monthly | Commerce analytics |
| Native mobile SDK installs | 100+ apps | SDK distribution |
| EU AI Act audit completions | 100% of commerce transactions | Compliance monitoring |

---

## 11. Appendix: Research Sources

### Product Documentation
- Google GECX Chat Widget Deployment: Deploy the chat client (web widget) documentation
- Google GECX Widget Tool: Using the widget tool documentation
- Google GECX Product Page: Gemini Enterprise for Customer Experience

### Competitive Intelligence
- Amazon Rufus: 250M+ users, $10B+ incremental annualized sales, 50+ technical upgrades in 2025
- ChatGPT Shopping: Instant Checkout (Sep 2025), Shopping Research (Nov 2025), 50M purchase-intent interactions/day
- Perplexity Shopping: Free shopping agent (Nov 2025), PayPal integration, 780M queries/month
- Klarna AI: APP launch (Dec 2025), 100M+ products, 800 FTE equivalent AI replacement then hybrid pivot
- Shopify Sidekick: Winter '26 Edition, Agentic Storefronts, MCP Server
- Salesforce Agentforce: $125/user/mo, Atlas Reasoning Engine, 70% resolution rate, Agent Script
- Microsoft Copilot: Dynamics 365 Contact Center, rich messaging, Copilot Checkout (Jan 2026)
- Zendesk: Resolution-based pricing ($1.50-$2/AR), Copilot add-on
- Intercom Fin: $0.99/resolution, standalone deployment, sub-1-hour setup
- Freshworks Freddy: Vertical AI agents, $0.50/interaction, 80% query resolution claimed
- Twilio Flex: ConversationRelay, BYO-LLM, programmable CX

### Protocol & Standards
- Google UCP: Announced NRF 2026 (Jan 11, 2026), open-source Apache 2.0, ucp.dev
- Google AP2: Agent Payments Protocol with cryptographic Mandates
- Google A2A: Agent-to-Agent protocol, 50+ partners
- OpenAI ACP: Agentic Commerce Protocol with Stripe, launched Sep 2025
- Klarna APP: Agentic Product Protocol, 100M+ products, 12 markets
- Visa TAP: Trusted Agent Protocol with Cloudflare, Oct 2025
- Mastercard Agent Pay: Acceptance framework for AI agents, Apr 2025
- MCP: Model Context Protocol, 97M+ monthly SDK downloads, donated to Linux Foundation
- Agentic AI Foundation: Linux Foundation governance body

### Market Data
- McKinsey: $3-5T consumer + $15T B2B agent-intermediated commerce by 2030
- Gartner: $80B in agent labor savings by 2026; Strategic Predictions 2026
- Precedence Research: $7.6B (2025) → $236B (2034) AI agents market
- Adobe/Salesforce: Cyber Week 2025 — AI influenced 20% of orders (~$67B)
- Consumer surveys: 44% comfortable with AI shopping (59% ages 18-34)
- Voice commerce: $116.8B → $714.5B by 2034
- Conversational AI market: $19.2B → $132.9B by 2034 (24% CAGR)

### Futures Research
- Generative UI: Google Research demo, MCP Apps (SEP-1865), 6 competing frameworks
- Know Your Agent (KYA): Emerging trust framework for agent identity
- EU AI Act: High-risk provisions enforceable August 2, 2026
- Spatial computing: Apple visionOS 26, 3D in chat (11x conversion lift)
- Agent-to-agent commerce: Forrester predicts 1 in 5 sellers deploy counter-offer agents in 2026
- Protocol convergence: Industry expects consolidation to 2-3 protocols by end of 2027

---

*Document prepared: February 2026*
*Classification: CONFIDENTIAL — Google Internal*
*Product Area: GECX Chat SDK*
*Author: Chat SDK Product Lead*
*Review cycle: Quarterly (next review: May 2026)*
