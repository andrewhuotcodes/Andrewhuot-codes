# PRD-008: Mobile-First Responsive Design

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

Mobile devices account for over 60% of e-commerce traffic and over 70% of chat interactions in most enterprise deployments. Despite this, the current Chat SDK was designed desktop-first — its 400px fixed-width panel, hover-dependent interactions, and non-touch-optimized controls create a subpar mobile experience.

Mobile-first responsive design is not a feature — it's a design constraint that applies to every other feature in the roadmap. Every component, every widget, every interaction pattern must be designed for a 375px-wide touch screen first and enhanced for desktop second. This PRD establishes the responsive design system and constraints that all other features must follow.

---

## What Are We Building

A responsive design system that ensures the Chat SDK delivers an excellent experience across all viewport sizes, input methods, and device capabilities.

### Viewport Breakpoints

| Breakpoint | Width | Name | Layout Behavior |
|-----------|-------|------|-----------------|
| XS | 0-359px | Small phone | Full-screen chat overlay, single-column widgets |
| SM | 360-599px | Phone | Full-screen chat overlay, single-column widgets |
| MD | 600-959px | Tablet | Side panel (40% width), two-column widget layout |
| LG | 960px+ | Desktop | Floating panel (400px), multi-column widgets |

### Mobile Layout

On mobile (XS/SM), the chat widget transitions from a floating panel to a **full-screen overlay**:

```
┌──────────────────────────┐
│ ← Back   Shopping Help   │  Header bar with back nav
├──────────────────────────┤
│                          │
│  Message history         │  Full-viewport scrollable area
│  (scrollable)            │
│                          │
│  ┌────────────────────┐  │
│  │ Widget renders     │  │  Widgets use full width
│  │ single-column      │  │
│  └────────────────────┘  │
│                          │
├──────────────────────────┤
│ [📎] Type a message [➤] │  Fixed bottom input bar
├──────────────────────────┤
│  Quick action chips      │  Optional suggestion chips
└──────────────────────────┘
```

### Touch Optimization

- **Touch targets:** All buttons, links, and interactive elements are minimum 44×44 CSS pixels (WCAG 2.2 / Apple HIG)
- **Swipe gestures:** Horizontal swipe on product carousel, swipe down to minimize chat
- **Safe areas:** Respect `env(safe-area-inset-*)` for notched displays and home indicator
- **Virtual keyboard handling:** Input bar stays pinned above the virtual keyboard; message log scrolls to maintain visibility of the latest message
- **Pull to refresh:** Pull down in message log to check for new messages (when history is stale)

### Widget Responsive Behavior

Every built-in widget has mobile-specific layout rules:

| Widget | Desktop | Mobile |
|--------|---------|--------|
| Product Carousel | Horizontal scroll, 3+ cards visible | Horizontal scroll, 1.2 cards visible (peek effect) |
| Product Comparison | Side-by-side table | Stacked cards with swipe between products |
| Checkout Flow | Multi-column (summary + form) | Single-column stacked steps |
| Form | Two-column field layout | Single-column full-width fields |
| Fulfillment Picker | Inline date/time picker | Native date picker (`<input type="date">`) |
| Cart View | Items + summary side by side | Items above, summary pinned below |

### Performance on Mobile

- **Network-aware loading:** On slow connections (via Network Information API), defer non-critical assets and use smaller image sizes
- **Battery-aware behavior:** On low battery (via Battery API), disable animations and reduce polling frequency
- **Memory management:** Virtualize messages and widgets outside the viewport to keep memory under 15MB on mobile

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Mobile Lighthouse performance score | >90 | Lighthouse CI |
| Mobile CLS (Cumulative Layout Shift) | <0.1 | Core Web Vitals |
| Mobile INP (Interaction to Next Paint) | <200ms | Core Web Vitals |
| Touch target compliance | 100% of interactive elements ≥44×44px | Automated scanning |
| Virtual keyboard message visibility | 100% — last message visible above keyboard | Manual QA |

### Success Criteria

1. A user on an iPhone SE (375px width) can complete the full commerce journey — browse products, compare, checkout — without pinch-zooming or encountering cut-off content.
2. The SDK passes Google's Mobile-Friendly Test.
3. Core Web Vitals (LCP, CLS, INP) are within "good" thresholds on a Moto G Power (mid-range Android device) on a 4G connection.
4. Every widget renders correctly at 375px width in both portrait and landscape orientations.

---

## Critical User Journeys

### CUJ 1: Mobile Shopping on iPhone
**Actor:** Consumer on iPhone 15 in portrait mode (393px width)
**Goal:** Buy a pair of shoes through the chat agent

1. User taps chat bubble → full-screen chat overlay opens with slide-up animation
2. Types "Show me running shoes under $150" using on-screen keyboard
3. Input bar stays pinned above keyboard; message log scrolls up
4. Agent responds with product carousel → user swipes through cards horizontally
5. Taps a shoe → product details widget fills the screen with image, price, sizes
6. Selects size → adds to cart → cart view shows items and total
7. Taps "Checkout" → single-column checkout flow: shipping → payment → confirm
8. Google Pay button renders full-width → user authenticates with Face ID
9. Order confirmation displays with tracking info
10. User taps ← Back → returns to the merchant's product page

### CUJ 2: Comparison Shopping on Android
**Actor:** Consumer on a Pixel 8 comparing laptops
**Goal:** Compare three laptops side by side

1. Agent sends a product comparison widget with 3 laptops
2. On mobile, comparison renders as stacked cards (not a table — tables are unreadable at 393px)
3. User swipes between cards: Laptop A ← → Laptop B ← → Laptop C
4. Key specs are highlighted on each card
5. "Compare side by side" option opens a full-screen overlay with a scrollable comparison table
6. User selects the winner and taps "Add to Cart"

### CUJ 3: Virtual Keyboard Interaction
**Actor:** Any mobile user typing a message
**Goal:** Message input remains usable when virtual keyboard opens

1. User taps the message input field
2. Virtual keyboard slides up
3. Input bar remains visible immediately above the keyboard
4. Message log scrolls up so the most recent message is still visible
5. User types and sends a message
6. New messages appear above the input bar (not hidden behind the keyboard)
7. User taps outside the input or presses the keyboard dismiss button
8. Keyboard slides down; chat layout returns to normal with animation

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Widget renders full-screen overlay on viewports <600px | P0 |
| FR-2 | Widget renders side panel on viewports 600-959px | P0 |
| FR-3 | Widget renders floating panel on viewports ≥960px | P0 |
| FR-4 | Input bar stays pinned above virtual keyboard on iOS and Android | P0 |
| FR-5 | Message log scrolls to latest message when keyboard opens | P0 |
| FR-6 | All interactive elements have minimum 44×44px touch target | P0 |
| FR-7 | Product carousel supports horizontal touch swipe | P0 |
| FR-8 | Product comparison renders as swipeable stacked cards on mobile | P0 |
| FR-9 | Checkout flow renders as single-column stacked steps on mobile | P0 |
| FR-10 | Layout respects `env(safe-area-inset-*)` for notched displays | P0 |
| FR-11 | `viewport` property in WidgetContext reports current breakpoint | P0 |
| FR-12 | Viewport changes (resize, orientation change) update layout without page reload | P0 |
| FR-13 | Swipe down gesture minimizes the chat on mobile | P1 |
| FR-14 | Form fields use native input types on mobile (date picker, phone keyboard) | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Lighthouse mobile performance score >90 | P0 |
| NFR-2 | CLS <0.1 on mobile viewports | P0 |
| NFR-3 | INP <200ms on Moto G Power (mid-range Android) | P0 |
| NFR-4 | All CSS uses relative units (rem/em/%) — no fixed pixel values for layout | P0 |
| NFR-5 | Tested on: iPhone SE, iPhone 15 Pro, Pixel 8, Galaxy S24, iPad Air | P0 |
| NFR-6 | Images served at 2x for retina, 1x for standard DPI | P1 |

---

## Open Questions

1. **Should mobile use a bottom sheet or full-screen overlay?** Bottom sheets (like Google Maps) allow partial visibility of the host page. Full-screen is simpler but hides context. Recommend: full-screen for phones, bottom sheet as a P2 enhancement.

2. **How do we handle the iOS Safari address bar?** Safari's address bar hides and shows during scroll, causing viewport height changes. The `dvh` (dynamic viewport height) unit helps but isn't supported on all browsers. Recommend: use `dvh` with `vh` fallback; test extensively on Safari.

3. **Should we support landscape mode?** Landscape on phones has very limited vertical space (~320px). Most chat apps don't optimize for landscape. Recommend: support it (don't break) but don't optimize for it in Phase 1. Show a "rotate for best experience" hint.

4. **Offline message queuing on mobile?** Mobile connections are unreliable. Should the SDK queue messages locally when offline and send them when connectivity returns? Recommend: yes, queue up to 10 messages in IndexedDB with retry on reconnection. P1 priority.

---

## Dependencies

- **Widget Registry (PRD-003):** Widgets receive viewport info via WidgetContext
- **Accessibility (PRD-005):** Touch targets overlap with a11y requirements
- **All widget PRDs:** Every widget must implement responsive behavior per this spec

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Responsive design system defined | April 2026 Week 1 | Breakpoints, layout modes, touch targets documented |
| Mobile layout implemented | April 2026 Week 3 | Full-screen overlay, input bar, safe areas working |
| Widget responsive behavior | May 2026 | All 12 built-in widgets have mobile layouts |
| Device testing | June 2026 | Tested on 5+ physical devices |
| GA with SDK v2 | July 2026 | Mobile-first from day one |
