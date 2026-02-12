# PRD-016: Generative UI Pipeline

**Phase:** 2 — "Make It Intelligent" | **Priority:** P0 | **Quarter:** Q4 2026
**Pillar:** Extensible Widgets | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Widget Registry (PRD-003) provides a powerful system for pre-built and custom widgets. But it has a ceiling: if the agent's intent doesn't match any registered widget type, the system falls back to an error card. Every uncovered intent is a dead end.

Generative UI eliminates that ceiling. When the agent declares a UI intent that doesn't match a registered widget, the SDK uses Gemini to generate an appropriate interactive interface on the fly — a comparison table, a scheduling calendar, a location picker, a decision matrix — rendered in a sandboxed container with the SDK's theme and accessibility constraints.

This is the highest-risk, highest-reward feature in the roadmap. If it works, the SDK can render anything. If it doesn't meet production quality standards, registered widgets still handle all common cases perfectly.

---

## What Are We Building

A pipeline that takes an agent's unresolved UI intent and produces a rendered, interactive, accessible widget using Gemini's code generation capabilities.

### Pipeline Architecture

```
Agent emits: { widget_type: 'delivery_schedule', data: {...} }
        │
        ▼
Widget Registry: No 'delivery_schedule' registered
        │
        ▼ (fallback)
Generative UI Pipeline:
  1. Template Match — check if a similar widget was recently generated and cached
  2. If cache miss → Generate — send intent + data + constraints to Gemini
  3. Gemini returns: { html, css, js, aria }
  4. Validate — lint HTML, check a11y metadata, verify no dangerous patterns
  5. Render — inject into sandboxed iframe with SDK theme applied
  6. Cache — store the generated template for reuse
        │
        ▼
Widget renders in the chat thread
```

### Generation Prompt (Conceptual)

```
Generate an interactive widget for the following intent:

Intent: delivery_schedule
Data: {
  "dates": ["2026-03-15", "2026-03-16", "2026-03-17"],
  "windows": [{"label": "9am-12pm", "available": true}, ...],
  "merchant": "Kroger"
}

Constraints:
- Must use these CSS custom properties for theming: [list]
- Must be responsive (works at 360px and 960px width)
- Must include ARIA roles and labels
- Must not use external resources (CDN, images, fonts)
- Must not execute network requests
- Must emit events via parent.postMessage for user interactions
- Output: { html: string, css: string, js: string, aria: { role, label } }
```

### Safety and Quality Guardrails

Generated code passes through validation before rendering:

1. **HTML sanitization:** Strip `<script src>`, `<iframe>`, `<object>`, `<embed>`, event handler attributes (`onclick`, etc.)
2. **CSS validation:** No `position: fixed`, no `z-index` above container, no external `@import`
3. **JS sandboxing:** Executed inside a sandboxed iframe with no access to parent DOM
4. **Accessibility check:** Verify ARIA role exists, at least one focusable element, contrast ratios meet AA
5. **Size limit:** Generated code must be <50 KB total (HTML + CSS + JS)
6. **Timeout:** Generation must complete within 3 seconds; fallback to a structured data display after timeout

### Caching Strategy

Most widget intents are repetitive — "product comparison" looks similar whether it's for laptops or blenders. The pipeline caches generated templates by a combination of widget type + data schema hash. If a new request matches a cached template's schema shape, the cached template is reused with new data injected, skipping generation entirely.

Expected cache hit rate: >70% after warm-up period.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Generation latency (P95) | <3 seconds (including Gemini call) | Performance monitoring |
| Cache hit rate | >70% after 30 days | Cache analytics |
| Render success rate | >95% (generated widgets render without errors) | Error tracking |
| Accessibility compliance of generated widgets | >80% pass automated a11y checks | axe-core on generated output |
| User interaction rate | Within 20% of equivalent registered widgets | Widget analytics comparison |
| Fallback rate (generation fails → error card) | <5% | Error tracking |

### Success Criteria

1. An agent can request a widget type that doesn't exist in the registry, and a usable, themed, accessible widget appears in <3 seconds.
2. Generated widgets look consistent with registered widgets (same colors, typography, spacing).
3. Generated widgets are safe — no XSS, no data leakage, no network access.
4. When generation fails or times out, the system gracefully falls back to a structured data display (not a blank space or error).

---

## Critical User Journeys

### CUJ 1: Novel Widget Rendered on the Fly
**Actor:** User asking about delivery options
**Goal:** See a delivery scheduling interface that doesn't exist as a built-in widget

1. User: "When can I get this delivered?"
2. Agent has delivery data but no `delivery_schedule` widget is registered
3. Agent emits: `{ widget_type: 'delivery_schedule', data: { dates: [...], windows: [...] } }`
4. Registry misses → Generative UI pipeline activates
5. Skeleton placeholder appears while Gemini generates the widget
6. After ~2 seconds, a calendar-like date picker renders with available windows
7. User taps "March 16, 9am-12pm" → event sent back to agent
8. Agent: "I've scheduled your delivery for March 16 between 9am and 12pm."

### CUJ 2: Cache Hit for Common Pattern
**Actor:** Second user asking about delivery (same merchant)
**Goal:** Instant rendering from cached template

1. User asks about delivery → same `delivery_schedule` intent
2. Registry misses → pipeline checks cache → cache hit (same schema shape)
3. Cached template is reused with new data → renders in <200ms (no Gemini call)
4. User sees the same quality widget, instantly

### CUJ 3: Generation Failure Fallback
**Actor:** User asking about something the pipeline can't generate well
**Goal:** Graceful degradation

1. Agent emits a complex widget intent with deeply nested data
2. Pipeline attempts generation → Gemini output fails validation (missing ARIA, oversized)
3. Fallback activates: data is rendered as a structured key-value display (formatted JSON-like card)
4. User sees the information in a readable format, just not as an interactive widget
5. Error event logged for pipeline improvement

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Pipeline activates when Widget Registry has no match and no registered fallback | P0 |
| FR-2 | Generated code is validated: HTML sanitized, CSS constrained, JS sandboxed | P0 |
| FR-3 | Generated widgets render in a sandboxed iframe (not in the main DOM) | P0 |
| FR-4 | SDK theme tokens are applied to generated widgets via CSS custom properties | P0 |
| FR-5 | Generated widgets communicate user interactions via `postMessage` | P0 |
| FR-6 | Template caching by widget_type + schema shape hash | P0 |
| FR-7 | Generation timeout at 3 seconds with fallback to structured data display | P0 |
| FR-8 | Accessibility validation of generated output (ARIA role, focusable elements) | P0 |
| FR-9 | Generated code size limit: 50 KB total | P0 |
| FR-10 | Developers can disable Generative UI via config (`generativeUI: false`) | P1 |
| FR-11 | Generation telemetry: latency, cache hit/miss, validation pass/fail | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | P95 generation latency <3 seconds (end-to-end including Gemini API call) | P0 |
| NFR-2 | P95 cached render latency <200ms | P0 |
| NFR-3 | Generated widgets cannot make network requests (CSP enforced in iframe) | P0 |
| NFR-4 | Generated widgets cannot access parent DOM or parent JavaScript context | P0 |
| NFR-5 | Pipeline module is <10 KB gzipped (excluding Gemini API client) | P1 |

---

## Open Questions

1. **Should we use Gemini Flash or Pro for generation?** Flash is faster (~500ms) but lower quality. Pro is slower (~2s) but produces better code. Recommend: Flash for simple intents (forms, lists), Pro for complex intents (interactive visualizations), with automatic routing.

2. **How do we handle iterative refinement?** If the first generation fails validation, should we retry with error feedback? Recommend: one retry with the validation error included in the prompt. If retry fails, fallback to structured data.

3. **Should generated widgets be saveable as registered widgets?** If a generated widget works well, the developer might want to "promote" it to a registered widget for faster loading. Recommend: yes, provide a `exportGeneratedWidget()` method that returns the generated template as a WidgetDefinition.

4. **Cost management.** Each Gemini call has a cost. For high-traffic deployments, generation costs could be significant. Recommend: aggressive caching + rate limiting (max N generations per session) + the option to pre-generate and register widgets for known intents.

---

## Dependencies

- **Widget Registry (PRD-003):** Pipeline is the fallback renderer
- **Iframe Sandbox (PRD-007):** Generated code runs in sandboxed iframes
- **Accessibility (PRD-005):** Generated widgets must meet a11y standards
- **Theme Tokens (PRD-003):** Generated widgets use SDK theme
- **Gemini API:** Code generation backend

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Generation prompt engineering | September 2026 | Prompt tested on 50+ intent types |
| Validation pipeline | October 2026 | HTML/CSS/JS/a11y validation working |
| Caching system | October 2026 Week 3 | Template cache with schema-shape matching |
| End-to-end pipeline | November 2026 | Generate → validate → render → interact |
| Quality benchmarking | November 2026 Week 3 | Compare generated vs. registered widget quality |
| GA | December 2026 | Shipped with Phase 2 |
