# The Chat SDK is a Renderer, Not an App

*A position paper on what the GECX Chat SDK should become, and what it should refuse to become.*

---

There's something deeply wrong with how we think about chat widgets.

Open any enterprise SaaS product's "chat" feature and you get a floating bubble in the bottom-right corner, a text input, and a scrolling list of messages. Maybe some "rich cards" — a carousel of products, a confirmation button, a star rating. The widget is a thin skin over a messaging API, deployed by pasting a `<script>` tag into a page, and then mostly forgotten.

This was fine when chatbots were flowcharts with personality. It is not fine when the thing on the other end of the conversation is a Gemini-class model that can reason about your purchase history, negotiate a bundle discount, compare products across three retailers, and execute a checkout — all within a single turn.

The GECX Chat SDK today has two JavaScript methods and four events. Two methods. Let that sink in. We built a protocol (UCP) that can orchestrate the entire commerce lifecycle — discovery, comparison, checkout, fulfillment, returns — and the front-end surface through which users actually experience it exposes `renderCustomText()` and `renderCustomCard()`. It's like building a Ferrari engine and bolting it to a skateboard.

This paper argues for a specific vision of what the Chat SDK should become, and — equally important — what it should not become. Because the biggest risk isn't building too little. It's building the wrong thing.

---

## The Leaky Abstraction at the Heart of Chat

Here's the core problem, stated plainly: **the current SDK pretends that agent output is messages, but agent output is increasingly actions.**

When the Shopping Agent finds you three suitcases and wants to show a comparison, that's not a "message" — it's a structured data payload that needs a specific UI treatment. When UCP returns a checkout session in `requires_escalation` state, the SDK needs to render an embedded merchant experience via JSON-RPC 2.0, track the session state machine, and return the user to the conversational flow afterward. When AP2 generates a CheckoutMandate — a cryptographically-signed consent artifact — the SDK needs to present it as a clear, signable card with the exact line items, totals, and payment method the user is authorizing.

None of this is "chat." It's a real-time, agent-composed application rendered within a conversation frame.

The mental model that gets this right is: **the Chat SDK is a renderer, not an app.** It takes structured declarations from agents and protocols and turns them into interactive UI. It does not own business logic. It does not make decisions. It renders what it's told to render, handles user interactions, and reports them back.

This is the same insight that made React successful. React didn't try to be an application framework — it was a rendering library. "Just the V in MVC," as they said. The components are pure functions of their props. The Chat SDK should work the same way: agents declare intent, the SDK renders it.

```
Agent Intent (structured JSON)
        │
        ▼
┌───────────────────┐
│  Widget Registry   │  ← resolves intent to component
├───────────────────┤
│  Renderer          │  ← sandboxed, accessible, themed
├───────────────────┤
│  Interaction Bus   │  ← captures user actions, reports back
└───────────────────┘
```

This architecture has a name. I've been calling it **"the declarative surface"** — the agent declares what it wants the user to see and do, and the SDK figures out how to render it. The agent never touches the DOM. The SDK never touches business logic. Clean separation. Testable. Auditable. Secure.

---

## What I Got Wrong the First Time

I wrote a roadmap for the Chat SDK. It had 44 features across three phases, five strategic pillars, and more competitive intelligence tables than a McKinsey deck. And when I re-read it with fresh eyes, I realized several things were wrong.

### Wrong #1: Accessibility was completely absent

This is embarrassing. We're building a Google enterprise product. The European Accessibility Act took effect June 2025. WCAG 2.2 AA isn't a nice-to-have — it's a legal requirement in every market we care about. The current SDK docs don't even mention ARIA roles. Our `<chat-messenger>` component uses a Shadow DOM with no documented keyboard navigation, no `role="log"` on the message container, no focus management on open/close, and no screen reader support.

There are 4,000+ ADA digital accessibility lawsuits per year and growing. Chat widgets specifically are cited for keyboard traps and inaccessible close buttons. Microsoft Teams has full JAWS/NVDA/Narrator/VoiceOver support. Salesforce bakes accessibility into its component library at the framework level. Intercom has published a WCAG 2.2 VPAT.

We have... nothing. This isn't a feature to be prioritized. It's a P0 blocker that should have been addressed years ago, and it moves to the top of Phase 1.

### Wrong #2: I forgot about streaming

The most fundamental UX pattern in modern AI chat is token-by-token response streaming. Every consumer has been trained by ChatGPT, Gemini, Claude, and Perplexity to expect text appearing word by word. If our SDK renders agent responses as complete blocks that appear all at once after a loading spinner, the experience feels broken regardless of what else we build.

Streaming is not just about perceived latency (though it is — time-to-first-token is more important than total response time for user satisfaction). It's about the architectural assumption that messages are complete atomic units. They're not. A streamed response might start as text, then emit a structured widget declaration mid-stream, then continue with text. The renderer needs to handle this gracefully.

```typescript
// The agent stream might look like this:
{ type: 'text_delta', content: 'I found three suitcases that match. Here\'s a comparison:\n\n' }
{ type: 'widget', widget_type: 'product_comparison', data: { products: [...] } }
{ type: 'text_delta', content: '\nThe Monos carry-on has the best reviews for your budget.' }
```

The SDK needs a streaming message renderer that can interleave text deltas and widget declarations in real time. This is harder than it sounds — you need to handle partial JSON, backpressure from slow renderers, and the case where a widget declaration spans multiple stream chunks.

### Wrong #3: The Transaction Audit Trail was in Phase 3

I put the Transaction Audit Trail — a complete, immutable log of every agent action, user consent, and commerce transaction — in Q1 2027. The EU AI Act high-risk provisions are enforceable **August 2, 2026**. That's a six-month gap where we'd be shipping commerce capabilities without the compliance infrastructure to support them in Europe.

This needs to be Phase 1. Not because compliance is exciting, but because it's architecturally load-bearing. If you design the event system without audit logging from the start, retrofitting it later means touching every event emitter in the codebase. Build the audit trail into the event bus from day one and it's nearly free. Add it later and it's a rewrite.

### Wrong #4: Too many features, not enough focus

44 features in 12 months. Let's be honest: that's roughly 3.5 features per month for what is presumably a team of 10-20 engineers. Some of these "features" — like a Generative UI Pipeline or Cross-Merchant Cart — are each multi-quarter projects on their own.

And some of the features were wrong for this product entirely:

- **Spatial Computing Surface** — Apple Vision Pro has sold roughly 1 million units. That's a rounding error. This is a forward bet for 2028, not a 2027 deliverable.
- **Kiosk & In-Car SDK** — If we build the API right, partners build these surfaces. We shouldn't be in the kiosk hardware business.
- **B2B Procurement Workflows** — This is a vertical application, not an SDK feature. If the Widget Registry works, someone else will build procurement widgets.
- **Widget Marketplace** — You can't have a marketplace before you have a widget ecosystem. This is a Phase 4 concept at the earliest.

Cut them. Ship fewer things, better. I'd rather ship 25 features that work flawlessly than 44 features where half are half-baked.

### Wrong #5: Mobile was in Phase 2

Mobile devices account for over 60% of e-commerce traffic. Treating mobile-responsive design as a Phase 2 "optimization" is backwards — it should be a design constraint from the first line of CSS. Every component, every widget, every interaction pattern should be designed mobile-first and enhanced for desktop. This isn't a feature. It's a design philosophy applied to every feature.

---

## What the Right Plan Looks Like

After the self-critique, the revised plan has three phases and roughly 30 features. Here's the logic.

### The Iron Triangle of Phase 1

Phase 1 has exactly three goals. If we nail these three things and nothing else, we win.

**1. The SDK becomes programmable.** Full JavaScript API. 30+ events. Lifecycle control. Session management. Conversation history. This is the foundation everything else requires. Without it, the SDK is a toy.

**2. The SDK becomes a commerce surface.** UCP inline checkout. AP2 consent flows. Google Pay integration. The embedded checkout bridge for `requires_escalation`. This is our raison d'être — if UCP exists but users can't check out inside the chat, UCP is academic.

**3. The SDK becomes trustworthy.** Accessibility. Security. Audit logging. Iframe sandboxing. These aren't features — they're the minimum bar for an enterprise product that handles commerce transactions. Ship commerce without trust infrastructure and we get sued, hacked, or both.

Everything in Phase 1 serves one of these three goals. If a feature doesn't serve one of them, it waits.

### The Bet of Phase 2

Phase 2 makes the bet that separates us from every competitor: **the SDK becomes a declarative surface for agent-composed UI.**

This means:
- The Widget Registry goes live, and developers can register custom widgets
- The Generative UI pipeline lets agents compose novel interfaces for intents that don't have registered widgets
- Multi-agent threads make the GECX "unified commerce + service" vision tangible — shopping and service agents collaborate in one thread, visibly, with smooth handoffs
- ACP compatibility makes us protocol-agnostic — merchants on UCP or ACP or both can all render checkout in our SDK

Phase 2 is where we stop being "a chat widget" and become "the agentic commerce surface." The widget registry is the key architectural decision — once custom widgets work, the ecosystem can build everything we cut from the roadmap (B2B procurement, kiosk UIs, vertical-specific widgets) without us.

### The Scaling of Phase 3

Phase 3 scales what works: native mobile SDKs, BigQuery analytics export, real-time monitoring, the proactive engagement engine. These are features that matter at 200+ enterprise deployments but not at 5. Build them when they're needed.

---

## The Architecture, From First Principles

Let me get concrete. The Chat SDK v2 is, at its core, three systems:

### System 1: The Event Bus

Everything flows through events. Agent messages, user actions, widget interactions, commerce state changes, session lifecycle — all events, all typed, all auditable.

```typescript
interface ChatEvent<T = unknown> {
  id: string;                    // UUID, globally unique
  type: string;                  // namespaced: 'message:received', 'commerce:checkout-started'
  timestamp: number;             // Unix ms
  source: 'agent' | 'user' | 'system' | 'widget';
  sessionId: string;
  conversationId: string;
  payload: T;
  metadata?: Record<string, unknown>;
}

// The audit trail is just a durable subscriber to the event bus.
// If you design this right, audit logging is one line:
eventBus.subscribe('*', auditLogger);
```

Every event gets a UUID and a timestamp. The audit trail is just a durable subscriber to `*`. This is why I said audit logging is nearly free if you design it in from day one — it's just another consumer of the event stream. Add it later and you're instrumenting every component individually.

The event bus also solves analytics. Commerce funnel analysis? Subscribe to `commerce:*` events and build a state machine. Widget engagement tracking? Subscribe to `widget:interaction` events. Agent performance metrics? Subscribe to `message:*` events and compute response times.

### System 2: The Widget Registry

This is the architectural heart of the declarative surface concept.

```typescript
interface WidgetDefinition<TData = unknown, TAction = unknown> {
  type: string;                           // e.g., 'product_comparison', 'checkout_flow'
  version: string;                        // semver
  schema: JSONSchema;                     // validates incoming data
  render: (container: HTMLElement, data: TData, context: WidgetContext) => void | (() => void);
  onAction?: (action: TAction) => void;   // handles user interactions
  accessibility?: {
    role: string;                         // ARIA role
    label: string | ((data: TData) => string);
    announceOnRender?: string | ((data: TData) => string);  // screen reader announcement
  };
}

interface WidgetContext {
  theme: ThemeTokens;                     // CSS custom properties
  locale: string;                        // BCP 47 language tag
  direction: 'ltr' | 'rtl';
  viewport: 'mobile' | 'tablet' | 'desktop';
  emit: (event: string, payload: unknown) => void;  // send events back to the bus
}

// Registration is one call:
chatSDK.registerWidget({
  type: 'product_comparison',
  version: '1.0.0',
  schema: productComparisonSchema,
  render: (container, data, ctx) => {
    // ... render comparison table
  },
  accessibility: {
    role: 'table',
    label: (data) => `Comparison of ${data.products.length} products`,
    announceOnRender: (data) => `Showing comparison of ${data.products.map(p => p.name).join(', ')}`,
  },
});
```

Notice that accessibility metadata is part of the widget definition, not an afterthought. The registry validates it. If you register a widget without accessibility metadata, it emits a console warning in development and a telemetry event in production. We can track the accessibility coverage of the widget ecosystem over time.

The resolution logic when an agent emits a UI intent:

```
1. Agent emits: { widget_type: 'product_comparison', data: {...} }
2. Registry looks up 'product_comparison'
   a. Found → validate data against schema → render in sandboxed container
   b. Not found → fall back to Generative UI pipeline (Phase 2)
   c. Schema validation fails → render error card + emit error event
3. User interacts → widget calls ctx.emit() → event bus → agent receives action
```

Built-in widgets ship as registered widgets using the same API that third-party developers use. No privileged internal APIs. This means anyone can override a built-in widget by registering their own widget with the same type name, which gives merchants full control of their brand experience.

### System 3: The Commerce Engine

The commerce engine is a state machine that tracks UCP checkout sessions and presents them through the widget system.

```typescript
// UCP checkout states map to SDK states:
type CheckoutState =
  | { status: 'browsing' }                    // no active checkout
  | { status: 'cart_open'; cart: CartState }   // items added, no checkout initiated
  | { status: 'incomplete'; session: UCPCheckoutSession; missing: string[] }
  | { status: 'requires_escalation'; session: UCPCheckoutSession; continueUrl: string }
  | { status: 'ready_for_complete'; session: UCPCheckoutSession }
  | { status: 'completed'; orderId: string; confirmation: OrderConfirmation }
  | { status: 'error'; error: CommerceError };

interface CartState {
  merchants: MerchantCart[];    // cross-merchant: each merchant has its own cart
  totalItems: number;
  estimatedTotal: Money;
}

interface MerchantCart {
  merchantId: string;
  merchantName: string;
  items: LineItem[];
  subtotal: Money;
  discounts: Discount[];
  fulfillmentOptions?: FulfillmentOption[];
  checkoutSessionId?: string;  // UCP session ID, if checkout has started
}
```

The cross-merchant cart is the important design decision here. UCP checkout sessions are per-merchant — you can't have a single checkout session spanning Walmart and Target. So the SDK maintains a unified cart as a convenience abstraction, but when the user clicks "Checkout," it creates separate UCP sessions per merchant and walks the user through them sequentially (or, in the future, in parallel tabs).

The `requires_escalation` state gets special treatment. When UCP returns this state, it means the merchant's checkout flow needs human input that the agent can't handle — maybe a complex shipping configuration, an age verification step, or a custom product configuration. The SDK renders the merchant's embedded checkout in a sandboxed iframe, communicating via JSON-RPC 2.0:

```typescript
// Embedded checkout bridge
interface EmbeddedCheckoutBridge {
  // The SDK opens an iframe to the merchant's continueUrl
  open(continueUrl: string, sessionId: string): void;

  // JSON-RPC 2.0 messages between SDK and merchant iframe
  onMessage(handler: (message: JsonRpcMessage) => void): void;
  sendMessage(message: JsonRpcMessage): void;

  // When the merchant signals completion, the SDK closes the iframe
  // and returns the user to the conversation
  onComplete(handler: (result: CheckoutResult) => void): void;
}
```

This is the architectural equivalent of a browser-within-a-browser. The merchant gets full control of their checkout experience. The SDK gets the completion signal. The user stays in the conversation thread. Everyone wins.

---

## The Accessibility Architecture

I want to spend time on this because it's where most chat SDKs fail, and where we have an opportunity to set the industry standard.

There is no W3C ARIA pattern for chat interfaces. The closest building blocks are `role="log"` (ARIA 1.2, technique ARIA23) for the message history and `role="dialog"` for the widget container. We need to compose these into a coherent accessibility architecture:

```html
<!-- The chat widget container -->
<div role="complementary" aria-label="Chat with shopping assistant">

  <!-- Header with controls -->
  <div role="toolbar" aria-label="Chat controls">
    <button aria-label="Minimize chat">...</button>
    <button aria-label="Close chat">...</button>
  </div>

  <!-- Message history - the key element -->
  <div role="log"
       aria-label="Conversation history"
       aria-live="polite"
       aria-relevant="additions"
       tabindex="0">
    <!-- Messages are list items for structure -->
    <div role="listitem" aria-label="Shopping Assistant, 2:34 PM">
      I found three suitcases that match your requirements.
    </div>
    <!-- Widgets within messages get their own ARIA roles -->
    <div role="listitem" aria-label="Shopping Assistant, 2:34 PM">
      <div role="table" aria-label="Comparison of 3 suitcases">
        <!-- widget content -->
      </div>
    </div>
  </div>

  <!-- Status area -->
  <div role="status" aria-live="polite">
    <!-- "Agent is typing..." announced by screen reader without focus change -->
  </div>

  <!-- Input area -->
  <form role="form" aria-label="Send a message">
    <input type="text"
           aria-label="Type a message"
           aria-describedby="char-count">
    <span id="char-count" aria-live="off">0/500 characters</span>
    <button type="submit" aria-label="Send message">...</button>
  </form>
</div>
```

The keyboard navigation contract:

```
Tab order: trigger button → header controls → message log → input → send → trigger
Escape: closes/minimizes widget, returns focus to trigger button
Arrow Up/Down: navigate between messages when log is focused
Enter/Space: activate focused message's interactive elements
Home/End: jump to first/last message
```

Every widget registered via the Widget Registry must provide accessibility metadata. The registry enforces this at validation time. In development mode, widgets without proper ARIA roles get a yellow border and a console warning. In production, they still render but emit a telemetry event so we can track ecosystem accessibility coverage.

This is how you make accessibility a platform guarantee rather than a per-feature checkbox: enforce it at the framework level, provide good defaults, and make the right thing the easy thing.

---

## The Streaming Renderer

This is the part most chat SDKs get wrong, and it matters more than people think.

The naive approach: wait for the complete agent response, then render it. This gives you a loading spinner for 2-5 seconds, then a wall of text appears all at once. Users hate this. It violates the expectations set by ChatGPT, Gemini, and every other AI product they've used.

The slightly-less-naive approach: stream text token by token. This is better, but it breaks when the response contains structured widgets. You're streaming "I found three suitcases..." and then suddenly the stream emits a `product_comparison` widget declaration. If you've been appending text to a `<p>` tag, you now need to split the paragraph, insert a widget, and continue appending text. Messy.

The right approach: **a streaming message renderer that treats every response as a sequence of typed blocks.**

```typescript
type StreamBlock =
  | { type: 'text_delta'; content: string }
  | { type: 'text_end' }
  | { type: 'widget_start'; widget_type: string }
  | { type: 'widget_data'; data: string }      // may arrive in chunks
  | { type: 'widget_end' }
  | { type: 'thinking_start' }                 // agent reasoning (may be hidden)
  | { type: 'thinking_end' };

class StreamingMessageRenderer {
  private currentBlock: 'text' | 'widget' | 'thinking' | null = null;
  private textBuffer: string = '';
  private widgetDataBuffer: string = '';
  private widgetType: string = '';

  processBlock(block: StreamBlock): void {
    switch (block.type) {
      case 'text_delta':
        if (this.currentBlock !== 'text') {
          this.flushCurrentBlock();
          this.currentBlock = 'text';
          this.createTextContainer();
        }
        this.appendText(block.content);
        break;

      case 'widget_start':
        this.flushCurrentBlock();
        this.currentBlock = 'widget';
        this.widgetType = block.widget_type;
        this.widgetDataBuffer = '';
        this.createWidgetPlaceholder();   // shows a skeleton/shimmer
        break;

      case 'widget_data':
        this.widgetDataBuffer += block.data;
        this.tryPartialWidgetRender();     // progressive rendering if possible
        break;

      case 'widget_end':
        this.finalizeWidget();             // full render with complete data
        this.currentBlock = null;
        break;

      // ... thinking blocks handled similarly
    }
  }

  private tryPartialWidgetRender(): void {
    // Some widgets can render progressively:
    // - Product carousel: show cards as they arrive
    // - Comparison table: show columns as they arrive
    // - Order summary: show line items as they arrive
    // Others must wait for complete data:
    // - Checkout flow: needs all data to present correctly
    // - AP2 mandate: must show complete, accurate info
  }
}
```

The widget placeholder (skeleton/shimmer) matters. When the stream indicates a widget is coming but data hasn't arrived yet, the user should see a ghost outline of the coming widget, not a blank space. This maintains the feeling of progressive rendering even for widgets that can't render partially.

Screen readers need special handling during streaming. You don't want the screen reader to announce every token — that would be an unlistenable wall of sound. Instead, buffer the text and announce complete sentences, or announce after a 500ms debounce, whichever comes first.

```typescript
class AccessibleStreamAnnouncer {
  private buffer: string = '';
  private debounceTimer: number | null = null;
  private readonly DEBOUNCE_MS = 500;

  appendText(text: string): void {
    this.buffer += text;

    // Announce on sentence boundaries
    if (/[.!?]\s*$/.test(this.buffer)) {
      this.announce();
      return;
    }

    // Or after 500ms of silence
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    this.debounceTimer = window.setTimeout(() => this.announce(), this.DEBOUNCE_MS);
  }

  private announce(): void {
    if (!this.buffer.trim()) return;
    // Update the aria-live region with the complete sentence/buffer
    this.liveRegion.textContent = this.buffer;
    this.buffer = '';
  }
}
```

---

## The Bundle Size Question

Here's a constraint that most roadmaps ignore but determines real-world adoption: **how big is this thing?**

The current SDK is loaded from Google's CDN via a single script tag. Every kilobyte of JavaScript we add increases load time for every page the widget appears on. For a commerce-critical e-commerce page, adding 200KB of JS to the critical path is a non-starter — it directly impacts Core Web Vitals, which directly impacts SEO, which directly impacts revenue.

My proposed budget:

```
Core runtime (event bus, message renderer, lifecycle):    ~30 KB gzipped
Widget registry + built-in text/card widgets:             ~15 KB gzipped
Accessibility layer (ARIA, keyboard, focus management):   ~8  KB gzipped
Theme engine:                                             ~5  KB gzipped
─────────────────────────────────────────────────────────
Initial bundle:                                           ~58 KB gzipped

Loaded on demand:
Commerce engine (UCP checkout, cart, payments):            ~25 KB gzipped
Individual widget renderers (per widget type):             ~3-8 KB each
Streaming renderer:                                        ~6  KB gzipped
Analytics collector:                                       ~4  KB gzipped
Voice input module:                                        ~12 KB gzipped
```

The architecture is code-split by design. The initial bundle — what loads when the script tag executes — is under 60 KB. Commerce modules load when the first commerce event fires. Widget renderers load when their widget type is first requested. Voice input loads when the user activates the microphone.

This means a site that uses the SDK for basic customer service chat loads ~58 KB. A site that uses it for full commerce loads ~90 KB. A site with voice loads ~100 KB. All reasonable for a CDN-hosted embed.

The key technique is **lazy widget loading:**

```typescript
// Widget renderers can be async
chatSDK.registerWidget({
  type: 'product_comparison',
  version: '1.0.0',
  schema: productComparisonSchema,
  // render can return a Promise — the registry shows a skeleton until it resolves
  render: async (container, data, ctx) => {
    const { renderComparison } = await import('./widgets/product-comparison.js');
    return renderComparison(container, data, ctx);
  },
  accessibility: { /* ... */ },
});
```

When the agent first requests a `product_comparison` widget, the registry shows a skeleton, lazy-loads the renderer, then renders the full widget. Subsequent requests use the cached module. The user sees a shimmer for ~100-200ms on first render, then instant rendering for all subsequent uses.

---

## What I Deliberately Left Out (And Why)

A good plan says no more often than it says yes. Here's what I cut from the original roadmap:

**Spatial Computing (visionOS/WebXR immersive mode).** Apple Vision Pro has ~1M units in the wild. Even if it 10x's in the next year, that's 10M units — smaller than the iPad's first year. I love the technology, but building a dedicated spatial computing surface for a chat SDK is premature optimization for a future that's 3-5 years away. If the Widget Registry is well-designed, someone will build a visionOS widget when the market is ready.

**Kiosk & In-Car SDK.** Same logic. If the SDK has a good API, partners build surfaces. Papa Johns doesn't need us to build a kiosk SDK — they need us to provide a headless API they can render in their own kiosk software. The renderer-not-app principle applies: we provide the rendering engine, they provide the surface.

**B2B Procurement Workflows.** RFQ management, bid comparison, and contract negotiation are vertical application features, not chat SDK features. They belong in a procurement product that uses the Chat SDK as its front-end, not in the SDK itself. If we build a Form widget and a Table widget and a Document Viewer widget, the B2B procurement app can compose them.

**Widget Marketplace.** You need an ecosystem before you need a marketplace. Phase 1 and 2 establish the Widget Registry and get third-party developers building widgets. The marketplace (discovery, installation, rating, revenue sharing) is a Phase 4 concept, probably 2028.

**Collaborative Shopping (shared threads with multiple users).** This is a compelling feature for social commerce, but the engineering complexity is enormous — real-time synchronization, conflict resolution, presence indicators, permissions. It's a standalone product initiative, not a roadmap line item.

**Countdown Timer widget.** I'm not building dark patterns into the SDK. If a merchant wants urgency marketing, they can build their own widget and register it. We don't ship it as a built-in.

---

## The Open Source Question

UCP is Apache 2.0. AP2 is open. A2A is open. MCP is donated to the Linux Foundation. Every protocol in our stack is open source.

Should the Chat SDK be open source too?

I think yes, and here's why.

**The strategic argument.** The more surfaces that render UCP, the more valuable UCP becomes. If the Chat SDK is open source, every developer who embeds it is an advertisement for UCP. Shopify merchants embed it. WordPress sites embed it. React developers use the React SDK. The widget becomes the ubiquitous front-end for Google's commerce infrastructure, which is exactly where we want to be.

**The trust argument.** Google has a well-earned reputation for killing products. Enterprise customers worry about betting on a Google API that might be deprecated. Open-sourcing the SDK (under Apache 2.0, same as UCP) sends the strongest possible signal: even if Google changes direction, the community can fork and maintain the SDK. This directly addresses the #1 enterprise objection to adopting GECX.

**The ecosystem argument.** A closed SDK means we build every widget ourselves. An open SDK means the community builds widgets we'd never think of — scheduling widgets for healthcare, document review widgets for legal, sensor data widgets for IoT. The Widget Registry is designed for extensibility; open source lets that extensibility actually happen.

**The quality argument.** Open source code gets scrutinized by more eyeballs. Security vulnerabilities get found faster. Accessibility issues get reported by the people who actually need accessibility. Performance regressions get caught by developers who care about their page load times.

The risk — that competitors fork the SDK and build on our work — is real but manageable. The SDK is the front-end; the value is in the platform (Gemini models, CX Agent Studio, Shopping Graph, UCP merchant network). Open-sourcing the renderer doesn't give away the engine.

My recommendation: open source the core SDK and widget registry under Apache 2.0. Keep the commerce engine (UCP integration, AP2 mandates, Google Pay) as a Google-hosted module loaded from our CDN. This gives the community the rendering layer while keeping the commerce integration proprietary.

---

## The Revised Roadmap: 28 Features, Three Phases

Here's the plan, after cutting the fat.

### Phase 1: "Make It Real" (Q2-Q3 2026)

Phase 1 answers one question: **can a user discover, compare, and purchase a product entirely within the chat thread?**

| # | Feature | Why |
|---|---------|-----|
| 1 | **SDK v2 Core API** — lifecycle, messaging, context, session | Everything else requires this |
| 2 | **Event Bus** with typed events, audit logging, and analytics hooks | Foundation for observability and compliance |
| 3 | **Widget Registry** with 12 built-in widgets + custom registration | Unlocks all future UI |
| 4 | **Streaming Message Renderer** with text/widget interleaving | Modern AI UX expectations |
| 5 | **Accessibility Layer** — WCAG 2.2 AA, keyboard nav, screen reader, VPAT | Legal requirement, enterprise blocker |
| 6 | **UCP Inline Checkout** — cart, checkout flow, payment selector | Core commerce value prop |
| 7 | **AP2 Consent Flows** — mandate cards with cryptographic signing | Required for UCP transactions |
| 8 | **Embedded Checkout Bridge** for `requires_escalation` | Handles hybrid agent/human checkout |
| 9 | **Google Pay Integration** | Default payment path |
| 10 | **Transaction Audit Trail** | EU AI Act compliance (Aug 2026) |
| 11 | **Iframe Sandbox Mode** | Enterprise security |
| 12 | **Multilingual Rich Content** (10 languages) | Global deployment blocker |
| 13 | **Mobile-First Responsive Design** | 60%+ of e-commerce traffic |
| 14 | **TypeScript + React SDKs** | Developer experience |
| 15 | **Conversation History API** with persistence | Cross-session continuity |

**Exit criteria:** A user on a Kroger or Lowe's site can discover products, compare them, check out with Google Pay, and return to the same conversation next week to check order status. The entire flow is keyboard-navigable and screen reader-accessible.

### Phase 2: "Make It Intelligent" (Q4 2026)

Phase 2 answers: **can the SDK render anything an agent can imagine?**

| # | Feature | Why |
|---|---------|-----|
| 16 | **Generative UI Pipeline** — AI-rendered widgets for novel intents | Eliminates widget coverage ceiling |
| 17 | **Multi-Agent Thread** with identity, handoff UI, and agent roster | GECX differentiator |
| 18 | **ACP Compatibility Layer** | Protocol-agnostic commerce |
| 19 | **Cross-Merchant Cart** | Shopping Graph monetization |
| 20 | **Proactive Engagement Engine** — intent signals + triggers | Reactive → anticipatory |
| 21 | **Image Understanding + Visual Search** | Gemini multimodal advantage |
| 22 | **Voice-in-Chat** — inline voice with transcription | Multimodal parity |
| 23 | **Commerce Funnel Analytics** | Merchant ROI measurement |
| 24 | **Plugin Architecture** | Ecosystem enablement |
| 25 | **A2A + MCP Protocol Integration** | Multi-agent orchestration + tool connectivity |

**Exit criteria:** An agent can compose a UI that doesn't exist in the widget registry and the SDK renders it. Shopping and service agents hand off seamlessly in one thread. The same SDK renders UCP and ACP checkouts side by side.

### Phase 3: "Make It Scale" (Q1-Q2 2027)

Phase 3 answers: **can this be the default commerce surface for Google?**

| # | Feature | Why |
|---|---------|-----|
| 26 | **Native Mobile SDKs** (iOS + Android) | App integration for retail partners |
| 27 | **BigQuery Analytics Export** | Enterprise BI integration |
| 28 | **Real-Time Monitoring + Alerting** | Enterprise operational reliability |

Phase 3 is deliberately thin. By this point, the SDK should be mature and the focus shifts to scaling adoption, hardening reliability, and supporting the growing widget ecosystem. If Phase 2 goes well, the features that matter most in Phase 3 will be obvious from usage data — and they may not be the ones we'd predict today.

---

## How We Know This Is Working

One metric matters above all others: **Commerce GMV transacted through the Chat SDK.**

Not page views. Not conversations started. Not "engagement." Revenue. Actual dollars flowing through the conversation thread.

Everything else is a leading indicator in service of that metric:

| Leading Indicator | What It Tells Us | Target (EOY 2026) |
|---|---|---|
| UCP checkout completion rate | Is the commerce flow good enough? | >65% |
| Time-to-first-widget-render (P95) | Is the performance acceptable? | <300ms |
| Accessibility audit score (axe-core) | Are we legally compliant? | 100% pass rate |
| Developer NPS | Do developers like building on this? | >40 |
| Custom widget registrations | Is the ecosystem growing? | 50+ in production |
| Multi-agent thread conversion rate | Does commerce+service help? | >15% lift vs. single-agent |
| Proactive engagement acceptance rate | Are the nudges helpful or annoying? | >12% acceptance |

If GMV is growing and these indicators are green, we're building the right thing. If GMV is flat, no amount of green indicators saves us — we've built a technically impressive product that doesn't drive commerce. In that case, we need to question the thesis, not add more features.

---

## The Honest Assessment

Let me be direct about the risks I'm most worried about.

**Risk #1: Generative UI might not be production-ready in 2026.** The Google Research demo was impressive. But going from a research demo to a production system that renders trustworthy, accessible, performant UI — in a commerce context where mistakes cost money — is a very different problem. The current Generative UI prototype generates HTML that sometimes has broken accessibility, sometimes renders incorrectly on mobile, and sometimes produces layouts that look nothing like the rest of the chat thread. My hedge: the Widget Registry with registered widgets is the primary path; Generative UI is the fallback for uncovered intents. If Generative UI isn't ready, registered widgets still work perfectly.

**Risk #2: Protocol fragmentation might not resolve.** UCP, ACP, APP, TAP — I said we should be protocol-agnostic, and I believe that. But what if a third protocol emerges that's structurally incompatible? What if ACP evolves in a direction that can't be rendered through the same widget system? My hedge: the widget-based architecture is inherently protocol-agnostic because widgets don't know about protocols. The commerce engine translates protocol state into widget data. Adding a new protocol means writing a new translator, not redesigning the UI.

**Risk #3: We might be too late.** ChatGPT processes 50 million purchase-intent interactions daily. We process... significantly fewer through the Chat SDK. The consumer habit of "ask ChatGPT" is forming right now, and habits are sticky. My honest take: we're not competing with ChatGPT for consumer shopping. We're competing for the enterprise surface — the Kroger app, the Lowe's website, the Papa Johns ordering system. In enterprise, relationships and integration depth matter more than consumer habit. We have the enterprise relationships. But we need to ship Phase 1 fast, before those customers get frustrated and build their own.

**Risk #4: This plan requires the team to execute flawlessly.** 15 features in Phase 1 across two quarters is aggressive. Some of these — UCP inline checkout, the streaming renderer, the accessibility layer — are individually complex projects. If the team is understaffed, something will ship half-baked. I'd rather cut features than ship broken ones. The ordered priority list exists for exactly this reason — if we can only ship 10 of 15 features in Phase 1, we ship features 1-10 and push 11-15 to Phase 2.

---

## The Punchline

The GECX Chat SDK is sitting in the most interesting position in all of enterprise software right now. We have the protocols (UCP, AP2, A2A). We have the models (Gemini). We have the data (Shopping Graph). We have the enterprise relationships (Kroger, Lowe's, Walmart, Target, Papa Johns). We have the payment infrastructure (Google Pay). We have the distribution (billions of searches, 650M+ Gemini users).

What we don't have is the surface. The place where all of this comes together for the human sitting on their couch, trying to buy a suitcase.

That surface is the Chat SDK. It's 58 kilobytes of JavaScript that translates agent intelligence into human experience. It's the declarative surface where Gemini's reasoning meets a user's intent and a merchant's catalog, and something happens — a product gets compared, a checkout gets initiated, a mandate gets signed, an order gets confirmed.

Build the renderer right and everything else clicks. Build it wrong — or don't build it fast enough — and the protocols, the models, and the data don't matter, because nobody can use them.

Two methods and four events. That's what we have today.

Let's fix that.

---

*February 2026*
