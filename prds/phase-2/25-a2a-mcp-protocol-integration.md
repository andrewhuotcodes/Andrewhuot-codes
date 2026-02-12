# PRD-025: A2A + MCP Protocol Integration

**Phase:** 2 — "Make It Intelligent" | **Priority:** P1 | **Quarter:** Q4 2026
**Pillar:** Multi-Agent | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

Google's Agent-to-Agent (A2A) protocol enables agents to discover each other, negotiate capabilities, and delegate tasks. The Model Context Protocol (MCP) — now with 97M+ monthly SDK downloads and donated to the Linux Foundation — enables agents to connect to external tools and data sources. Together, they form the multi-agent orchestration layer.

The Chat SDK needs to surface A2A agent interactions and MCP tool usage within the conversation thread, making the multi-agent architecture visible and understandable to users.

---

## What Are We Building

### A2A Integration

When the primary agent discovers and delegates to an external agent (via A2A), the SDK:
- Shows the external agent's identity (name, capabilities, trust status)
- Renders the delegation as a visible handoff (similar to multi-agent thread, PRD-017)
- Displays the external agent's responses within the same thread
- Shows task status updates for long-running delegated tasks

### MCP Tool Visualization

When an agent uses MCP tools (database queries, API calls, document retrieval), the SDK can optionally display tool usage:

```
┌──────────────────────────────────────┐
│ 🛒 Shopping Assistant                │
│                                      │
│ Let me check that for you...         │
│                                      │
│ ┌────────────────────────────────┐   │
│ │ 🔧 Using: Inventory Checker   │   │  ← MCP tool usage
│ │    Checking stock at 3 stores  │   │     (collapsible)
│ │    ✓ Store A: In stock         │   │
│ │    ✓ Store B: In stock         │   │
│ │    ✗ Store C: Out of stock     │   │
│ └────────────────────────────────┘   │
│                                      │
│ Great news! That item is available   │
│ at 2 nearby stores.                  │
└──────────────────────────────────────┘
```

Tool usage visualization is collapsible (hidden by default, expandable for users who want transparency) and configurable (can be disabled entirely for simpler UX).

### Agent Discovery Card

When A2A discovers a relevant external agent, the SDK can present it:

```
┌──────────────────────────────────────┐
│ 🔍 Found: FedEx Tracking Agent      │
│    Can track packages and estimate   │
│    delivery times.                   │
│    [Connect] [Not now]               │
└──────────────────────────────────────┘
```

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| A2A delegations visible in thread | >90% of A2A tasks display status | Protocol analytics |
| MCP tool usage display adoption | >30% of deployments enable tool viz | Configuration tracking |
| User trust in multi-agent delegation | >70% positive sentiment | Post-conversation survey |

### Success Criteria

1. Users can see when external agents are involved in their conversation and understand what those agents are doing.
2. MCP tool usage is transparent (viewable on demand) but not intrusive (collapsed by default).
3. A2A agent handoffs work as smoothly as internal agent handoffs (PRD-017).

---

## Critical User Journeys

### CUJ 1: Agent Delegates to Shipping Specialist via A2A
**Actor:** User tracking a delivery
**Goal:** Get delivery status from an external logistics agent

1. User: "Where's my package?"
2. Shopping agent discovers a FedEx tracking agent via A2A
3. Thread shows: "Connecting to FedEx Tracking Agent..."
4. FedEx agent responds with tracking status, rendered in the thread
5. User sees delivery estimate without leaving the conversation

### CUJ 2: Transparent Tool Usage
**Actor:** Curious user who wants to understand agent reasoning
**Goal:** See what tools the agent used to answer their question

1. User: "Is the Ninja blender in stock near me?"
2. Agent uses MCP to query inventory API
3. Collapsible tool card shows: "Using Inventory Checker — checking 3 stores"
4. Results populate: 2 in stock, 1 out of stock
5. User expands the card to see details, building trust in the agent's answer

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | A2A agent delegation renders as a visible handoff in the thread | P0 |
| FR-2 | External agent identity (name, capabilities) displayed | P0 |
| FR-3 | A2A task status updates shown inline (pending, running, complete) | P0 |
| FR-4 | MCP tool usage rendered as collapsible cards in the thread | P1 |
| FR-5 | Tool visualization is configurable (on/off/collapsed-by-default) | P1 |
| FR-6 | Agent discovery cards allow user to accept or decline external agents | P1 |
| FR-7 | All A2A/MCP events flow through the Event Bus | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | A2A/MCP module is lazy-loaded (~8 KB gzipped) | P0 |
| NFR-2 | Tool visualization cards render in <200ms | P0 |
| NFR-3 | Accessible: tool cards are keyboard-navigable, expand/collapse announced by screen reader | P0 |

---

## Open Questions

1. **Should users be able to block specific A2A agents?** Recommend: yes, via an "agent preferences" setting. Phase 3 enhancement.
2. **MCP tool error display.** If an MCP tool call fails, should the error be shown to the user? Recommend: show a generic "couldn't complete this check" message; detailed errors in collapsible section for debugging.
3. **Trust levels for A2A agents.** How do we convey trust (verified vs. unverified external agents)? Recommend: align with KYA framework. Verified agents get a badge; unverified agents show a caution indicator.

---

## Dependencies

- **Multi-Agent Thread (PRD-017):** A2A handoffs use the same handoff UI
- **Event Bus (PRD-002):** A2A/MCP events
- **Widget Registry (PRD-003):** Tool cards are registered widgets
- **A2A Protocol backend:** Agent discovery and delegation
- **MCP runtime:** Tool execution

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| A2A handoff display | October 2026 | External agent delegation visible in thread |
| MCP tool visualization | November 2026 | Collapsible tool usage cards |
| Agent discovery cards | November 2026 Week 3 | User-approved external agent connections |
| GA | December 2026 | Shipped with Phase 2 |
