# PRD-005: Accessibility Layer (WCAG 2.2 AA)

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Trust | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Chat SDK has no documented accessibility support. The `<df-messenger>` web component uses Shadow DOM with no published ARIA patterns, no keyboard navigation contract, no screen reader testing, and no VPAT (Voluntary Product Accessibility Template). This is a legal and reputational risk for Google and for every enterprise that deploys the SDK.

The European Accessibility Act (EAA) took effect June 28, 2025. The Americans with Disabilities Act (ADA) generates 4,000+ digital accessibility lawsuits per year, with chat widgets specifically cited for keyboard traps and inaccessible dismiss buttons. Section 508 requires federal agencies and their vendors to meet WCAG standards. Enterprise customers like Kroger, Lowe's, and government-adjacent organizations will not deploy a widget that cannot produce a VPAT.

This is not a feature. It is a P0 legal compliance requirement and an enterprise sales blocker that should have been addressed years ago.

---

## What Are We Building

A comprehensive accessibility layer that makes the Chat SDK conform to WCAG 2.2 Level AA, including keyboard navigation, screen reader support, focus management, motion sensitivity, and high contrast mode. The layer consists of three modules:

### 1. Keyboard Navigation Manager

Full keyboard control of the chat widget without a mouse:

| Key | Context | Action |
|-----|---------|--------|
| Tab | Anywhere | Move between major regions: trigger → header → message log → input → send button |
| Shift+Tab | Anywhere | Reverse tab order |
| Escape | Widget open | Close/minimize widget, return focus to trigger button |
| Arrow Up/Down | Message log focused | Navigate between messages |
| Home/End | Message log focused | Jump to first/last message |
| Enter/Space | Focused button/action | Activate the element |
| Ctrl+F6 | Anywhere in widget | Cycle between widget regions (header, log, input) |

Custom shortcuts can be registered by developers for widget-specific interactions.

### 2. Focus Management

- **Focus trap:** When the widget opens, focus moves into the widget and stays there until the widget is closed (prevents tabbing into the background page).
- **Focus restoration:** When the widget closes, focus returns to the element that had focus before the widget opened (typically the trigger button).
- **Focus on new messages:** When a new agent message arrives, focus does not jump to it (would be disruptive), but the message is added to the `aria-live` region for screen reader announcement.
- **Focus on widget open:** Focus moves to the message input field (most common user intent on open).

### 3. Screen Reader Support

ARIA role architecture:

```html
<div role="complementary" aria-label="Chat with shopping assistant">
  <div role="toolbar" aria-label="Chat controls">
    <button aria-label="Minimize chat">...</button>
    <button aria-label="Close chat">...</button>
  </div>

  <div role="log" aria-label="Conversation history"
       aria-live="polite" aria-relevant="additions" tabindex="0">
    <div role="listitem" aria-label="Shopping Assistant, 2:34 PM">
      Message content here
    </div>
    <div role="listitem" aria-label="You, 2:35 PM">
      Your message here
    </div>
  </div>

  <div role="status" aria-live="polite">
    <!-- "Shopping Assistant is typing..." -->
  </div>

  <form role="form" aria-label="Send a message">
    <input type="text" aria-label="Type a message"
           aria-describedby="char-count">
    <span id="char-count" aria-live="off">0/500 characters</span>
    <button type="submit" aria-label="Send message">...</button>
  </form>
</div>
```

### 4. Widget Accessibility Contract

Every widget registered via the Widget Registry (PRD-003) must provide accessibility metadata:

- **role:** ARIA role for the widget's root element
- **label:** Accessible label (static or derived from data)
- **announceOnRender:** Text announced by screen reader when the widget first appears

The registry validates this on registration and logs warnings for missing metadata. In development mode, widgets without accessibility metadata render with a yellow debug border.

### 5. Additional Accessibility Features

- **High contrast mode:** Respects `prefers-contrast: more` and provides a manual toggle via `a11y.highContrast` config
- **Reduced motion:** Respects `prefers-reduced-motion: reduce` — disables typing animations, skeleton shimmers, and slide transitions
- **Text scaling:** All typography uses relative units (rem/em) and responds to browser text size settings up to 200%
- **Touch targets:** All interactive elements meet WCAG 2.2 minimum target size (24×24 CSS pixels, recommended 44×44)
- **Color contrast:** All text/background combinations meet 4.5:1 ratio (AA) minimum; large text meets 3:1

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| axe-core automated audit score | 100% pass (0 violations) | CI/CD automated testing |
| Manual screen reader test pass rate | 100% pass across NVDA, JAWS, VoiceOver, Narrator | QA manual testing |
| Keyboard-only task completion rate | 100% of tasks completable without mouse | Usability testing |
| VPAT published | Yes, publicly available | Documentation site |
| Color contrast violations | 0 across all themes | Automated scanning |

### Success Criteria

1. A screen reader user (NVDA on Windows, VoiceOver on macOS) can complete the full commerce CUJ — ask about a product, compare options, add to cart, initiate checkout — using only keyboard and screen reader.
2. A VPAT (WCAG 2.2 AA level) is published on the documentation site and can be shared with enterprise procurement teams.
3. axe-core runs in CI/CD and blocks deployment on any accessibility violation.
4. The accessibility module adds <8 KB gzipped to the initial bundle.

---

## Critical User Journeys

### CUJ 1: Screen Reader User Browses Products
**Actor:** Blind user using NVDA on Windows with Chrome
**Goal:** Ask the shopping agent about products and hear the results

1. User tabs to chat trigger button: NVDA announces "Chat with shopping assistant, button"
2. User presses Enter: widget opens, focus moves to input
3. NVDA announces "Chat with shopping assistant. Type a message, edit field"
4. User types "Show me wireless headphones under $100" and presses Enter
5. NVDA announces "You: Show me wireless headphones under $100" (from aria-live)
6. Typing indicator: NVDA announces "Shopping Assistant is typing"
7. Response streams (announced in sentence chunks by accessible announcer)
8. Product carousel renders: NVDA announces "Showing 4 wireless headphones under $100"
9. User presses Arrow Down to enter the carousel, Arrow Right/Left to browse products
10. NVDA announces each product: "Sony WH-1000XM4, $89.99, 4.7 stars, In Stock"

### CUJ 2: Keyboard-Only Checkout
**Actor:** Motor-impaired user who cannot use a mouse
**Goal:** Complete a purchase using only keyboard navigation

1. User navigates to checkout widget using Arrow keys
2. Tab navigates through checkout steps: shipping address → payment → review
3. Each form field is reachable via Tab with clear labels
4. Error messages are associated with fields via `aria-describedby`
5. "Place Order" button is focusable; Enter confirms
6. Confirmation is announced via aria-live region

### CUJ 3: Widget with Custom Accessibility
**Actor:** Developer building a custom appointment scheduler widget
**Goal:** Ensure the custom widget is accessible

1. Developer registers widget with accessibility metadata:
   ```javascript
   accessibility: {
     role: 'dialog',
     label: 'Schedule appointment',
     announceOnRender: 'Appointment scheduler opened. Use arrow keys to navigate dates.',
     managesFocus: true,
   }
   ```
2. Widget renders; screen reader announces the `announceOnRender` text
3. Since `managesFocus: true`, the widget handles its own internal keyboard navigation
4. When the user presses Escape within the widget, focus returns to the message log

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Widget container has `role="complementary"` with descriptive `aria-label` | P0 |
| FR-2 | Message history container has `role="log"` with `aria-live="polite"` | P0 |
| FR-3 | Typing indicators are announced via `role="status"` with `aria-live="polite"` | P0 |
| FR-4 | Input field has `aria-label`, associated character count, and form role | P0 |
| FR-5 | All buttons have accessible names (via aria-label or visible text) | P0 |
| FR-6 | Tab key navigates between major regions in logical order | P0 |
| FR-7 | Escape key closes the widget and restores focus to trigger | P0 |
| FR-8 | Arrow keys navigate between messages when log is focused | P0 |
| FR-9 | Focus is trapped within the widget when open (no tabbing to background) | P0 |
| FR-10 | Focus moves to input on widget open; restores to trigger on close | P0 |
| FR-11 | New messages are announced by screen reader without stealing focus | P0 |
| FR-12 | Widget Registry validates accessibility metadata on registration | P0 |
| FR-13 | All color combinations meet WCAG AA contrast ratios (4.5:1 normal, 3:1 large) | P0 |
| FR-14 | All interactive elements have minimum touch target 24×24 CSS px | P0 |
| FR-15 | Streaming text announcements are debounced (sentence boundaries or 500ms) | P0 |
| FR-16 | `prefers-reduced-motion` disables animations and transitions | P1 |
| FR-17 | `prefers-contrast` activates high contrast theme | P1 |
| FR-18 | Typography scales correctly up to 200% browser text size | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Accessibility module is <8 KB gzipped | P0 |
| NFR-2 | Loaded as part of the initial bundle (not lazy loaded — a11y must be immediate) | P0 |
| NFR-3 | axe-core automated tests run in CI/CD and block deployment on violations | P0 |
| NFR-4 | Manual screen reader testing covers NVDA, JAWS, VoiceOver, Narrator | P0 |
| NFR-5 | VPAT document is published and maintained | P0 |

---

## Open Questions

1. **Should the chat widget use `role="dialog"` or `role="complementary"`?** Dialog implies a modal overlay that traps focus. Complementary implies a sidebar-like region. The chat widget is non-modal when minimized but focus-trapping when open. Recommend: `role="complementary"` for the container, with focus trapping behavior managed programmatically.

2. **How do we test with screen readers in CI/CD?** Automated tools (axe-core) catch ~30% of accessibility issues. Manual screen reader testing is required but can't run in CI. Recommend: axe-core in CI, manual SR testing as a pre-release gate (not per-commit).

3. **How do we handle third-party widget accessibility?** We enforce metadata at registration, but we can't guarantee the widget's internal DOM is accessible. Recommend: provide an accessibility testing harness in the Widget SDK; publish an "Accessible Widget Checklist"; log violations in development mode.

4. **RTL layout testing.** Arabic, Hebrew, and Farsi require RTL layout. Do we have CI coverage for RTL rendering? Recommend: add RTL-specific visual regression tests.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Keyboard shortcuts registered via the API
- **Widget Registry (PRD-003):** Accessibility metadata is part of WidgetDefinition
- **Streaming Renderer (PRD-004):** Accessible announcer integrates with streaming
- **Theme Tokens (part of Widget Registry):** Color contrast enforcement

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| ARIA architecture design review | April 2026 Week 1 | Role assignments and keyboard contract finalized |
| Keyboard navigation implemented | April 2026 Week 3 | Tab order, arrow nav, escape, focus trap working |
| Screen reader testing (first pass) | May 2026 | NVDA + VoiceOver manual testing completed |
| axe-core CI integration | May 2026 Week 2 | Automated testing blocking deployment |
| VPAT draft | June 2026 | First draft of WCAG 2.2 AA conformance report |
| VPAT published | July 2026 | Final VPAT on documentation site at GA |
