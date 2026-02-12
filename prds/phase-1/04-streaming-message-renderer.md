# PRD-004: Streaming Message Renderer

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Developer Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

Every major AI chat product — ChatGPT, Gemini, Claude, Perplexity — renders responses token by token as they stream from the model. Users have been trained to expect this. A chat interface that shows a loading spinner for 3 seconds and then reveals a complete wall of text feels broken, regardless of how fast the total response time is.

The current Chat SDK renders agent responses as complete messages. There is no streaming support. This creates a perceptual latency gap that makes the GECX experience feel a generation behind consumer AI products.

More critically, streaming in an agentic commerce context is harder than simple text streaming. An agent response might start with text, emit a structured widget (product comparison table) mid-stream, continue with more text, and end with action buttons. The renderer must handle this interleaving gracefully — splitting text blocks, inserting widgets, and continuing text — all while maintaining accessibility and performance.

---

## What Are We Building

A streaming message renderer that processes agent responses as a sequence of typed blocks, rendering each block incrementally as it arrives.

### Block Types

```typescript
type StreamBlock =
  | { type: 'text_delta'; content: string }        // text token(s)
  | { type: 'text_end' }                           // end of text segment
  | { type: 'widget_start'; widget_type: string; instance_id: string }
  | { type: 'widget_data_delta'; data: string }    // widget data chunk (may need buffering)
  | { type: 'widget_end' }                         // widget data complete, render
  | { type: 'action_block'; actions: ActionButton[] }
  | { type: 'thinking_start' }                     // optional reasoning display
  | { type: 'thinking_delta'; content: string }
  | { type: 'thinking_end' }
  | { type: 'error'; code: string; message: string };
```

### Rendering Behavior

**Text blocks:** Append characters to the current text container with a typing animation. When `text_end` arrives, finalize the paragraph.

**Widget blocks:** When `widget_start` arrives, close any open text block, insert a skeleton placeholder (sized by `estimatedHeight`), and begin buffering `widget_data_delta` chunks. When `widget_end` arrives, parse the complete widget data, validate it, and render the widget via the Widget Registry. Some widgets support progressive rendering (`supportsStreaming: true`) — for these, attempt to render partial data as it arrives.

**Action blocks:** Render interactive buttons below the current content.

**Thinking blocks:** Optionally display agent reasoning in a collapsible section (configurable via `showThinking` in ChatSDKConfig).

### Text/Widget Interleaving Example

```
Stream:  text_delta("I found three suitcases")
         text_delta(" that match your requirements.\n\n")
         text_end
         widget_start("product_comparison", "widget-001")
         widget_data_delta('{"products":[{"name":"Monos...')
         widget_data_delta('..."}],"attributes":[...]}')
         widget_end
         text_delta("The Monos carry-on has the best ")
         text_delta("reviews in your budget range.")
         text_end
         action_block([{id:"add_monos", label:"Add to Cart", ...}])

Render:  ┌──────────────────────────────────┐
         │ I found three suitcases that     │  ← text rendered token-by-token
         │ match your requirements.          │
         │                                   │
         │ ┌─────────┬─────────┬──────────┐ │
         │ │ Monos   │ Away    │ Samsonite│ │  ← widget rendered when complete
         │ │ $295    │ $275    │ $249     │ │
         │ │ ★★★★★  │ ★★★★☆  │ ★★★★☆   │ │
         │ └─────────┴─────────┴──────────┘ │
         │                                   │
         │ The Monos carry-on has the best   │  ← text continues after widget
         │ reviews in your budget range.     │
         │                                   │
         │ [Add to Cart]                     │  ← action button
         └──────────────────────────────────┘
```

### Accessible Streaming

Screen readers cannot process token-by-token text — it would produce an unlistenable stream of individual words. The renderer includes an `AccessibleStreamAnnouncer` that:

1. Buffers streamed text
2. Announces on sentence boundaries (`.`, `!`, `?`)
3. Falls back to announcing after 500ms of silence
4. Announces widget arrivals: "Showing comparison of 3 suitcases"
5. Does not announce `thinking` blocks (configurable)

See [CHAT_SDK_TECHNICAL_SPEC.md §6](../../CHAT_SDK_TECHNICAL_SPEC.md#6-streaming-renderer-specification) for interface definitions.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Time-to-first-character | <50ms from stream start | Custom performance mark |
| Characters per second render rate | >200 chars/sec visually | Visual benchmark |
| Widget skeleton → full render time | <300ms (P95) | Performance marks |
| Layout shift during streaming (CLS) | <0.01 per stream | Cumulative Layout Shift measurement |
| Screen reader announcement latency | <1s from sentence completion to announcement | Manual SR testing |

### Success Criteria

1. Streaming text/widget interleaving renders without layout jank, as verified by Lighthouse CLS score <0.01 during a streaming response.
2. A NVDA user can understand a streamed response (with embedded widgets) as well as a sighted user, as verified by accessibility audit.
3. A response containing 3 text blocks, 1 widget, and 1 action block renders correctly end to end.

---

## Critical User Journeys

### CUJ 1: Token-by-Token Text Response
**Actor:** End user asking a question
**Goal:** See the agent's text response appear progressively

1. User sends "What's your return policy?"
2. Agent starts streaming: "Our return policy allows..."
3. User sees text appearing word by word with a blinking cursor indicator
4. Response completes; cursor disappears; response is added to conversation history

### CUJ 2: Streamed Response with Embedded Widget
**Actor:** End user comparing products
**Goal:** See text context around a product comparison table

1. User: "Compare these three laptops"
2. Stream begins: "Here's a comparison of the three laptops you're considering:"
3. Text finalizes, followed by a skeleton placeholder shimmer animation
4. Widget data streams in; skeleton transitions to full comparison table
5. Stream continues: "The MacBook Air offers the best value..."
6. Action buttons appear: [Add MacBook Air to Cart] [See More Details]

### CUJ 3: Screen Reader User Receives Streamed Response
**Actor:** Screen reader user (NVDA)
**Goal:** Hear the streamed response announced in readable chunks

1. Agent starts streaming a paragraph about return options
2. NVDA stays silent until the first sentence completes ("Our return policy allows returns within 30 days of purchase.")
3. NVDA announces the complete sentence
4. Second sentence completes; NVDA announces it
5. Widget arrives; NVDA announces "Showing return form"
6. User tabs into the widget to interact

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Renderer processes `text_delta` blocks and appends content to a text container with visual typing effect | P0 |
| FR-2 | Renderer processes `widget_start` / `widget_data_delta` / `widget_end` blocks, showing skeleton during buffering and rendering via Widget Registry on completion | P0 |
| FR-3 | Renderer handles text/widget interleaving — text before, between, and after widgets | P0 |
| FR-4 | Renderer processes `action_block` with interactive buttons | P0 |
| FR-5 | Renderer processes `thinking_start/delta/end` blocks with optional display (configurable) | P1 |
| FR-6 | Renderer processes `error` blocks with user-facing error card | P0 |
| FR-7 | `end()` method finalizes the stream and assembles the complete Message object | P0 |
| FR-8 | `abort()` method cancels the current stream and cleans up partial renders | P0 |
| FR-9 | Stream renderer emits `message:stream-start`, `message:stream-delta`, `message:stream-end` events | P0 |
| FR-10 | Accessible stream announcer buffers text and announces on sentence boundaries | P0 |
| FR-11 | Accessible stream announcer announces widget arrivals using `accessibility.announceOnRender` | P0 |
| FR-12 | Skeleton placeholders use `estimatedHeight` from widget definitions to minimize CLS | P1 |
| FR-13 | Widgets with `supportsStreaming: true` receive progressive data during streaming | P2 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Streaming renderer module is <6 KB gzipped | P0 |
| NFR-2 | Module is lazy-loaded on first `message:stream-start` event | P0 |
| NFR-3 | Text rendering does not block the main thread for >8ms per frame (60fps) | P0 |
| NFR-4 | Memory usage does not grow unboundedly during long streams | P0 |
| NFR-5 | Partial JSON in `widget_data_delta` is correctly buffered and concatenated | P0 |

---

## Open Questions

1. **What animation style for streaming text?** Options: (a) character-by-character (like a typewriter), (b) word-by-word, (c) chunk-by-chunk (as received). Recommend: word-by-word for readability, with the underlying data appended as received and visual animation smoothed.

2. **How do we handle a very large widget arriving mid-stream?** If a product comparison table with 20 products arrives, the skeleton might be significantly smaller than the final widget, causing a layout jump. Recommend: `estimatedHeight` as a function of data size, plus a smooth height animation on render.

3. **Should the typing indicator and stream coexist?** Currently, `typing:agent-start` shows a typing indicator. When streaming begins, should the indicator disappear? Recommend: yes, transition from typing indicator to streaming content.

4. **How do we handle stream reconnection?** If the WebSocket drops mid-stream, should the renderer retry or show an error? Recommend: show a "connection lost, reconnecting..." inline indicator and resume from the last received block.

---

## Dependencies

- **Event Bus (PRD-002):** Stream events flow through the bus
- **Widget Registry (PRD-003):** Widget blocks are rendered via the registry
- **Accessibility Layer (PRD-005):** Announcer integrates with the accessibility module
- **GECX backend:** Server-sent events or WebSocket stream endpoint

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Stream block protocol defined | April 2026 Week 1 | Block types and serialization format agreed with backend |
| Text streaming working | April 2026 Week 3 | Token-by-token text rendering with typing animation |
| Widget interleaving working | May 2026 | Text + widget + text renders correctly |
| Accessible announcer integrated | May 2026 Week 3 | Screen reader testing passed (NVDA, VoiceOver) |
| GA with SDK v2 | July 2026 | Shipped as lazy-loaded module |
