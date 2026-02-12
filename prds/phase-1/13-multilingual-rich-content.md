# PRD-013: Multilingual Rich Content

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q3 2026
**Pillar:** Extensible Widgets | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The current Chat SDK's rich content — widget labels, button text, system messages, error strings, accessibility labels — is English-only. This is a hard blocker for global customers. Woolworths Australia, Zalando (Europe), and other international partners cannot deploy the SDK until rich content renders in their users' languages.

Agent-generated text is already multilingual (Gemini handles translation). The gap is in the SDK's own UI strings: "Add to Cart," "Checkout," "Place Order," "Showing 4 products," screen reader announcements, error messages, date/number formatting, and RTL layout for Arabic/Hebrew.

---

## What Are We Building

A localization system that provides:

1. **SDK UI string translations** for 10 languages at launch
2. **Locale-aware formatting** for numbers, currencies, dates, and times
3. **RTL layout support** for Arabic and Hebrew
4. **Widget content localization** via the `WidgetContext.t()` function and `locale`/`direction` properties
5. **Dynamic language switching** via `chatSDK.setLanguage()`

### Launch Languages (10)

| Language | Code | RTL | Market Justification |
|----------|------|-----|---------------------|
| English | en | No | Default |
| Spanish | es | No | US Hispanic, Latin America |
| French | fr | No | Canada, France, Africa |
| German | de | No | DACH region |
| Japanese | ja | No | Japan market |
| Korean | ko | No | Korea market |
| Portuguese (BR) | pt-BR | No | Brazil market |
| Arabic | ar | Yes | Middle East, North Africa |
| Hebrew | he | Yes | Israel market |
| Chinese (Simplified) | zh-CN | No | China/Singapore market |

### String Catalog

All SDK UI strings are externalized into a string catalog with ICU MessageFormat support for pluralization and interpolation:

```typescript
// String catalog format
const en = {
  'chat.input.placeholder': 'Type a message',
  'chat.send': 'Send message',
  'chat.minimize': 'Minimize chat',
  'chat.close': 'Close chat',
  'cart.items': '{count, plural, one {# item} other {# items}} in cart',
  'cart.total': 'Total: {amount}',
  'checkout.step': 'Step {current} of {total}',
  'checkout.place_order': 'Place Order',
  'checkout.processing': 'Processing payment...',
  'mandate.authorize': 'Authorize',
  'mandate.decline': 'Decline',
  'mandate.expires': 'Expires in {time}',
  'product.add_to_cart': 'Add to Cart',
  'product.in_stock': 'In Stock',
  'product.out_of_stock': 'Out of Stock',
  'product.rating': '{score} out of {max} stars, {count} reviews',
  'a11y.new_message': '{agent} said: {preview}',
  'a11y.typing': '{agent} is typing',
  'a11y.widget_loaded': 'Showing {description}',
  'error.network': 'Connection lost. Reconnecting...',
  'error.generic': 'Something went wrong. Please try again.',
  // ~100 total strings
};
```

### Currency and Number Formatting

Uses `Intl.NumberFormat` and `Intl.DateTimeFormat` for locale-aware display:

```typescript
// In WidgetContext
function formatCurrency(amount: Money, locale: string): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: amount.currency,
  }).format(amount.amount / 100);
}

// Result:
// en-US: $79.99
// de-DE: 79,99 €
// ja-JP: ¥7,999
// ar-SA: ٧٩٫٩٩ ر.س
```

### RTL Layout

When the locale is `ar` or `he`, the entire chat widget mirrors:
- Message bubbles align to the right (agent) and left (user)
- Text direction is `rtl`
- Widget layouts flip (product carousels scroll right-to-left)
- Icons with directional meaning (arrows, send button) are mirrored

This is implemented via CSS logical properties (`margin-inline-start` instead of `margin-left`) and the `dir="rtl"` attribute on the widget container.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Languages available at GA | 10 | Configuration count |
| Untranslated strings in production | 0 | Automated string coverage check |
| RTL layout bugs | 0 critical/high | QA testing |
| Locale-specific formatting correctness | 100% for currencies, dates, numbers | Automated formatting tests |

### Success Criteria

1. A Japanese-speaking user sees all SDK UI strings (buttons, labels, system messages, screen reader text) in Japanese.
2. An Arabic-speaking user sees a fully mirrored RTL layout with Arabic strings.
3. Currency amounts display correctly for the user's locale (€79,99 not $79.99 for German users).
4. A developer can add a new language by providing a string catalog JSON file — no code changes.

---

## Critical User Journeys

### CUJ 1: German User Completes Purchase
**Actor:** Consumer on Zalando (German market)
**Goal:** Entire checkout experience in German

1. SDK initialized with `language: 'de'`
2. Chat input placeholder: "Nachricht eingeben"
3. Agent response is in German (handled by Gemini)
4. Product carousel labels: "In den Warenkorb" (Add to Cart)
5. Cart widget: "2 Artikel im Warenkorb" / "Gesamt: 89,99 €"
6. Checkout: "Schritt 1 von 3" / "Bestellung aufgeben"
7. Screen reader announces in German

### CUJ 2: Arabic RTL Layout
**Actor:** Consumer in Saudi Arabia
**Goal:** Chat widget renders correctly in RTL

1. SDK initialized with `language: 'ar'`
2. Entire widget mirrors: trigger button on left, text right-aligned
3. Message bubbles: agent on right side, user on left side
4. Product carousel scrolls right-to-left
5. Send button icon points left (mirrored)
6. Mandate card text is right-aligned with Arabic numerals option

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | All SDK UI strings are externalized into locale-specific string catalogs | P0 |
| FR-2 | String catalogs support ICU MessageFormat for pluralization and interpolation | P0 |
| FR-3 | 10 languages available at GA (see table above) | P0 |
| FR-4 | `chatSDK.setLanguage()` changes the locale at runtime without page reload | P0 |
| FR-5 | `WidgetContext.locale` and `WidgetContext.direction` are available to all widgets | P0 |
| FR-6 | `WidgetContext.t()` provides localized string lookup for widgets | P0 |
| FR-7 | Currency amounts formatted via `Intl.NumberFormat` with locale-appropriate symbols and separators | P0 |
| FR-8 | Dates formatted via `Intl.DateTimeFormat` with locale-appropriate format | P0 |
| FR-9 | RTL layout activated automatically for Arabic and Hebrew locales | P0 |
| FR-10 | CSS uses logical properties (`inline-start/end`) instead of physical (`left/right`) | P0 |
| FR-11 | String catalogs are lazy-loaded (only the active locale is loaded) | P1 |
| FR-12 | Developers can provide custom string catalogs for additional languages | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Each string catalog is <5 KB gzipped | P0 |
| NFR-2 | Language switch completes in <200ms (no flicker) | P0 |
| NFR-3 | All translated strings are reviewed by native speakers (not machine-translated) | P0 |
| NFR-4 | RTL visual regression tests in CI/CD | P0 |

---

## Open Questions

1. **Machine translation for additional languages?** For languages beyond the initial 10, should we accept machine-translated strings as a starting point? Recommend: no for SDK UI strings (quality is critical for brand trust). Developers can provide their own catalogs for additional languages.

2. **Plural rules beyond one/other?** Arabic has 6 plural forms. ICU MessageFormat handles this, but translators must provide all forms. Recommend: use ICU MessageFormat; include a translator guide with plural form requirements per language.

3. **Bi-directional text (mixed LTR/RTL)?** Product names might be in English while the UI is in Arabic. Recommend: use `<bdi>` elements for embedded opposite-direction text to prevent garbled rendering.

4. **Number formatting for screen readers.** `Intl.NumberFormat` produces visual text but screen readers may announce it differently. Recommend: provide `aria-label` with spelled-out numbers for accessibility-critical contexts (totals, mandate amounts).

---

## Dependencies

- **Widget Registry (PRD-003):** Widgets receive locale/direction via WidgetContext
- **Accessibility (PRD-005):** Screen reader announcements must be localized
- **All widget PRDs:** Every widget must use `t()` for UI strings and `Intl` for formatting

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| String catalog schema + extraction | June 2026 Week 1 | All ~100 strings externalized |
| English + 4 languages translated | July 2026 | EN, ES, FR, DE, JA available |
| RTL layout implementation | July 2026 Week 3 | Arabic/Hebrew layout working |
| All 10 languages translated and reviewed | August 2026 | Native speaker review complete |
| GA | September 2026 | 10 languages shipped |
