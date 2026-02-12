# PRD-015: Conversation History API

**Phase:** 1 — "Make It Real" | **Priority:** P1 | **Quarter:** Q3 2026
**Pillar:** Developer Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

Every conversation in the current SDK is ephemeral. Close the tab, lose the conversation. Return next week, start from zero. There is no conversation history API, no session persistence, and no cross-session continuity.

This is particularly damaging for commerce. A user who spent 15 minutes comparing products, built a cart, and then got distracted loses everything. A user who completed a purchase has no way to return to the same thread to ask about shipping or request a return.

The Conversation History API provides persistent, queryable, cross-session conversation storage. Users return and pick up where they left off. Agents have full context of previous interactions. Commerce sessions survive page refreshes and device switches.

---

## What Are We Building

A server-side conversation storage system (backed by Firestore) with a client-side API for reading, restoring, and managing conversation history.

### API Surface

```typescript
// Get history for the current conversation
const messages: Message[] = await chatSDK.getHistory();

// Restore a previous session (loads its conversation history)
await chatSDK.restoreSession(previousSessionId);

// Clear history for the current conversation
await chatSDK.clearHistory();

// Get session metadata (for building a session picker UI)
const sessions = await chatSDK.listSessions({ limit: 10 });
// Returns: [{ sessionId, startedAt, lastMessageAt, messageCount, preview }]
```

### Storage Model

```
Firestore Collection: conversations/{conversationId}
├── metadata: { userId, agentId, startedAt, lastMessageAt, messageCount }
├── messages/
│   ├── {messageId}: { role, blocks, timestamp, agent?, metadata? }
│   ├── {messageId}: { ... }
│   └── ...
└── commerce/
    ├── cart: { merchants, totalItems, estimatedTotal }
    └── checkouts/{sessionId}: { status, cart, fulfillment, mandates }
```

### Session Restoration Flow

1. User returns to the site → SDK checks for a saved session ID (cookie or localStorage)
2. If found: `restoreSession(sessionId)` is called automatically (configurable)
3. SDK fetches the conversation history from Firestore
4. Messages are rendered in the chat thread (most recent N visible, older messages loaded on scroll-up)
5. Cart and checkout state are restored
6. Agent receives the conversation context, enabling continuity: "Welcome back! You were looking at blenders last time."

### Privacy and Data Management

- History storage requires user authentication (no anonymous history to prevent data accumulation without identity)
- Users can clear their own history via the SDK or an in-chat action
- History respects the customer's configured data retention period
- GDPR deletion requests clear all conversation data for the specified user

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Session restoration rate | >50% of returning authenticated users resume a previous session | Session analytics |
| History load time (last 50 messages) | <500ms (P95) | Performance monitoring |
| Cross-session commerce completion | >10% of purchases involve returning to a previous session | Commerce analytics |
| User satisfaction with continuity | Measurable improvement in CSAT for returning users | CSAT surveys |

### Success Criteria

1. A user who left mid-checkout can return the next day, see their cart and conversation, and complete the purchase without repeating any steps.
2. History loads in <500ms for conversations with up to 100 messages.
3. Scroll-up pagination loads older messages without jank or duplicate rendering.
4. `clearHistory()` removes all data from Firestore within 24 hours.

---

## Critical User Journeys

### CUJ 1: Return Shopper Resumes Conversation
**Actor:** Authenticated user who was browsing products yesterday
**Goal:** Pick up where they left off

1. User visits the retailer's website (next day)
2. SDK finds a saved session ID → calls `restoreSession()`
3. Chat widget shows a subtle "Previous conversation restored" indicator
4. User opens chat → sees yesterday's conversation (last 20 messages visible)
5. Agent: "Welcome back! You were comparing the Ninja and KitchenAid blenders. Ready to decide?"
6. User: "Yes, I'll go with the Ninja"
7. Cart still has the Ninja blender from yesterday → proceeds to checkout

### CUJ 2: User Scrolls Through History
**Actor:** User wanting to find a product recommendation from last week
**Goal:** Scroll back through previous messages

1. User opens chat → sees recent messages
2. Scrolls up → older messages load in batches (20 at a time)
3. Loading spinner appears at the top while fetching
4. User finds the product recommendation from 5 days ago
5. Product carousel still interactive → user taps "Add to Cart"

### CUJ 3: User Clears History
**Actor:** Privacy-conscious user
**Goal:** Delete all conversation history

1. User opens chat settings (gear icon or menu)
2. Taps "Clear conversation history"
3. Confirmation dialog: "This will permanently delete all messages. This cannot be undone."
4. User confirms → history cleared → fresh conversation starts
5. All Firestore data for this user-conversation pair is deleted

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | `getHistory()` returns all messages for the current conversation | P0 |
| FR-2 | `restoreSession(sessionId)` loads a previous session's history and state | P0 |
| FR-3 | `clearHistory()` deletes all messages for the current conversation | P0 |
| FR-4 | Messages are stored in Firestore with the documented schema | P0 |
| FR-5 | Cart and checkout state are persisted alongside messages | P0 |
| FR-6 | Auto-restore: SDK automatically checks for and restores the most recent session on init (configurable) | P1 |
| FR-7 | Scroll-up pagination loads older messages in batches of 20 | P1 |
| FR-8 | `listSessions()` returns recent sessions with metadata and preview text | P1 |
| FR-9 | History requires authenticated user (no anonymous history) | P0 |
| FR-10 | Data retention respects customer-configured period (default: 90 days) | P1 |
| FR-11 | GDPR deletion: `deleteUserData(userId)` removes all data for a user | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | History load (50 messages) completes in <500ms (P95) | P0 |
| NFR-2 | Scroll-up pagination loads in <300ms per page | P0 |
| NFR-3 | Message write (new message to Firestore) completes in <200ms | P0 |
| NFR-4 | Storage cost is optimized: only message content + metadata stored (no rendered HTML) | P1 |
| NFR-5 | Works offline: messages queued in IndexedDB and synced when online | P2 |

---

## Open Questions

1. **Cross-device history.** If a user starts on mobile and continues on desktop, should they see the same history? This requires server-side storage keyed by user ID (not device/session). Recommend: yes, history is keyed by user ID + agent ID. Cross-device continuity is a key value prop.

2. **How many messages to load on restore?** Loading all messages for a months-old conversation could be slow. Recommend: load the most recent 20 messages; load more on scroll-up.

3. **Should widget state be restored?** If the last message contained a product carousel, should the carousel data be restored? Recommend: yes — messages store their blocks (including widget blocks with data). The Widget Registry re-renders them on restoration.

4. **Conversation expiry.** When does a "session" end and a new one begin? If the user returns after 30 days, should they see the old conversation or start fresh? Recommend: configurable session timeout (default: 7 days). After timeout, old session is archived but accessible; new session starts.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** History API methods on the ChatSDK interface
- **Event Bus (PRD-002):** `session:restored` event emitted on restoration
- **Commerce Engine (PRD-009):** Cart state restored alongside messages
- **Firestore:** Backend storage infrastructure
- **User authentication:** Required for persistent history

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Firestore schema defined | June 2026 Week 2 | Collection structure and indexes finalized |
| Message persistence working | July 2026 | Messages written and read from Firestore |
| Session restoration | August 2026 | Full session + cart restoration end-to-end |
| Scroll-up pagination | August 2026 Week 3 | Lazy loading of older messages |
| GA | September 2026 | Shipped with Phase 1 |
