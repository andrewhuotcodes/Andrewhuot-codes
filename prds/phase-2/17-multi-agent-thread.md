# PRD-017: Multi-Agent Thread

**Phase:** 2 — "Make It Intelligent" | **Priority:** P0 | **Quarter:** Q4 2026
**Pillar:** Multi-Agent | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

GECX's key architectural differentiator is unifying shopping and service agents in one platform. But the SDK currently has no concept of multiple agents. Every message appears to come from the same entity. When the shopping agent hands off to a returns specialist, there's no visible transition, no identity change, no context handoff indicator. The user has no idea they're talking to a different agent.

Multi-Agent Threads make the multi-agent architecture visible and trustworthy. Users see which agent is responding, understand when handoffs occur, and can see the roster of available agents. Agents share conversation context so the user never repeats themselves.

---

## What Are We Building

### Agent Identity in Messages

Every agent message includes visible agent identity:

```
┌──────────────────────────────────────┐
│ 🛒 Shopping Assistant               │  ← agent name + avatar
│ I found 3 blenders matching your    │
│ requirements.                        │
│ [Product Carousel]                   │
├──────────────────────────────────────┤
│ 🛒 Shopping Assistant               │
│ Great choice! Let me start checkout. │
├──────────────────────────────────────┤
│ ─── Transferring to Returns ─────── │  ← visible handoff indicator
├──────────────────────────────────────┤
│ 📦 Returns Specialist               │  ← different agent
│ Hi! I see you purchased the Ninja   │
│ blender 3 days ago. How can I help? │  ← has full context
└──────────────────────────────────────┘
```

### Handoff UI

When one agent transfers to another, the SDK renders a handoff indicator:
- Visual separator with transfer description ("Transferring to Returns Specialist")
- Brief context summary visible to the user ("They have your order history")
- Optional: reason for handoff ("Your question is about a recent order")
- Smooth transition animation

### Agent Roster

An expandable panel showing available/active agents in the thread:

```
┌────────────────────────────────┐
│ Agents in this conversation:   │
│                                │
│ 🛒 Shopping Assistant  Active  │
│ 📦 Returns Specialist  Ready  │
│ 💳 Payment Help       Ready   │
│                                │
│ ─────────────────────────────  │
│ Powered by Gemini              │
└────────────────────────────────┘
```

### Context Preservation

On handoff, the receiving agent gets:
- Full conversation history
- Cart state and checkout session
- User preferences and context
- Reason for handoff from the sending agent

The user never repeats information. This is the key UX promise.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Multi-agent thread adoption | 30% of enterprise deployments use multi-agent threads | Feature analytics |
| Handoff success rate | >95% of handoffs complete without user needing to repeat context | User surveys + agent logs |
| User satisfaction post-handoff | CSAT score within 10% of single-agent conversations | Post-conversation survey |
| Average handoff transition time | <3 seconds from initiation to receiving agent's first message | Timestamp analysis |
| Context preservation rate | >99% of handoffs include full conversation context | Agent logs |

### Success Criteria

1. A user transitions from a shopping agent to a returns specialist in one thread, and the returns specialist demonstrates awareness of the user's purchase history without the user explaining it.
2. The handoff is visually clear — the user can see which agent they're now talking to.
3. Agent identity is accessible to screen readers (agent name announced with each message).
4. Enterprise customers can configure 2-5 agents per thread with defined handoff rules.

---

## Critical User Journeys

### CUJ 1: Shopping → Post-Purchase Service
**Actor:** Consumer who bought a product and needs help
**Goal:** Transition from shopping to service without friction

1. User purchased a blender through the shopping agent last week
2. User returns to chat: "My blender arrived damaged"
3. Shopping agent recognizes this as a post-purchase issue
4. Handoff indicator: "Connecting you with our Returns Specialist... They have your order details."
5. Returns Specialist: "I'm sorry about that! I can see your order #KRG-789 for the Ninja blender delivered on March 12. Would you like a replacement or a refund?"
6. User never had to provide order number, product name, or purchase date

### CUJ 2: Proactive Agent Suggestion
**Actor:** User with a complex request spanning multiple domains
**Goal:** Get help from the right specialist without manual routing

1. User: "I want to set up a weekly grocery delivery"
2. Shopping agent finds relevant products
3. Agent identifies this also involves scheduling and payments: "I can help with the products. For setting up recurring delivery, let me bring in our Delivery Specialist."
4. Delivery Specialist joins the thread: "Hi! I can set up weekly delivery for the items [Shopping Assistant] selected. Let's pick a schedule."
5. Both agents are visible in the agent roster

### CUJ 3: Human Agent Escalation
**Actor:** User whose issue can't be resolved by AI agents
**Goal:** Smooth transition to a human agent

1. AI agent determines the issue requires human intervention
2. Handoff indicator: "I'm connecting you with a team member who can help with this."
3. Queue position displayed: "You're #3 in queue. Estimated wait: 2 minutes."
4. Human agent joins: "Hi, I'm Sarah. I've reviewed your conversation and I see you're having trouble with..."
5. Full conversation transcript is visible to the human agent

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Messages display agent identity (name, avatar, role badge) | P0 |
| FR-2 | Handoff between agents renders a visible transition indicator | P0 |
| FR-3 | Handoff includes context summary visible to the user | P0 |
| FR-4 | Receiving agent has full conversation history and context on handoff | P0 |
| FR-5 | Agent roster panel shows available/active agents | P1 |
| FR-6 | Handoff events (`agent:handoff-started`, `agent:handoff-completed`) are emitted | P0 |
| FR-7 | Human escalation shows queue position and estimated wait time | P1 |
| FR-8 | `agent:human-escalation` event emitted for CRM integration | P0 |
| FR-9 | Screen readers announce agent identity with each message | P0 |
| FR-10 | Agent identity includes verified badge (for KYA-verified agents, Phase 2+) | P2 |
| FR-11 | Cart and commerce state is preserved across agent handoffs | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Handoff transition renders in <500ms | P0 |
| NFR-2 | Agent roster is lazy-loaded (not part of initial bundle) | P1 |
| NFR-3 | Agent identity display adds <2 KB per agent to the bundle | P0 |
| NFR-4 | Multi-agent thread works correctly on mobile (full-screen overlay) | P0 |

---

## Open Questions

1. **Can multiple agents be active simultaneously?** In the current spec, only one agent responds at a time. Could two agents collaborate on a single response (e.g., shopping + payment agents answering together)? Recommend: Phase 2 supports sequential multi-agent (one active at a time with handoffs). Simultaneous multi-agent is a Phase 3+ research topic.

2. **How are handoff rules configured?** Enterprise customers need to define which agents can hand off to which others, and under what conditions. Recommend: handoff rules are configured in CX Agent Studio, not in the SDK. The SDK renders whatever handoff the backend initiates.

3. **What about agent impersonation?** If multiple agents are in the thread, how do we prevent a malicious agent from claiming to be a different agent? Recommend: agent identity is set by the backend (Conversational Agents Runtime), not by the agent itself. The SDK trusts the backend-provided identity.

4. **Thread branching.** Should the user be able to "go back" to a previous agent without going through the current one? Recommend: not in Phase 2. Linear thread with handoffs. Agent switching UI as a Phase 3 enhancement.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** Agent identity is part of the Message type
- **Event Bus (PRD-002):** Handoff events
- **Accessibility (PRD-005):** Agent identity must be announced by screen readers
- **Commerce Engine (PRD-009):** Commerce state preserved across handoffs
- **Audit Trail (PRD-006):** Handoffs are auditable events
- **GECX Conversational Agents Runtime:** Backend orchestrates agent handoffs

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Agent identity UI design | September 2026 | Agent avatars, badges, handoff indicator designs |
| Agent identity in messages | October 2026 | Messages display agent name and avatar |
| Handoff transition UI | October 2026 Week 3 | Animated handoff indicator with context summary |
| Agent roster panel | November 2026 | Expandable panel showing agent list |
| End-to-end handoff testing | November 2026 Week 3 | Shopping → Service handoff with context preservation |
| GA | December 2026 | Shipped with Phase 2 |
