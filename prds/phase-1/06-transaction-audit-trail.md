# PRD-006: Transaction Audit Trail

**Phase:** 1 — "Make It Real" | **Priority:** P0 | **Quarter:** Q2 2026
**Pillar:** Trust | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The EU AI Act high-risk provisions are enforceable **August 2, 2026**. AI systems that influence consumer purchasing decisions — which is exactly what a shopping agent does — fall under high-risk obligations including traceability, transparency, and human oversight. Without a complete audit trail of every agent action, user consent, and commerce transaction, GECX customers deploying in the EU face regulatory exposure.

This feature was originally planned for Phase 3 (Q1 2027) — six months after the EU AI Act enforcement date. That was wrong. The audit trail needs to ship with the first commerce capabilities, not after them.

The architectural insight that makes this feasible is that the Event Bus (PRD-002) already captures every action in the system. The audit trail is a durable subscriber to the event bus — a single `eventBus.onAny()` call that writes every event to an immutable log with tamper-detection hashes. Building this into the event bus from day one makes it nearly free. Retrofitting it later would mean instrumenting every component individually.

---

## What Are We Building

An immutable, tamper-evident log of every significant action within the Chat SDK, focused on commerce transactions and agent decisions. The audit trail captures what happened, when it happened, who was involved, and what the user consented to.

### Audit Record Schema

```typescript
interface AuditRecord {
  id: string;              // UUIDv7
  timestamp: string;       // ISO 8601
  eventType: string;       // from ChatEventMap
  eventId: string;         // reference to the source event
  sessionId: string;
  conversationId: string;
  userIdHash: string;      // pseudonymized user ID (SHA-256)
  agentId: string;
  agentRole: string;
  action: AuditAction;     // e.g., 'mandate_signed', 'payment_completed'
  outcome: 'success' | 'failure' | 'pending' | 'cancelled';
  commerce?: {
    merchantId?: string;
    checkoutSessionId?: string;
    mandateId?: string;
    mandateType?: 'intent' | 'checkout' | 'payment';
    amount?: Money;
    orderId?: string;
  };
  reasoning?: string;      // agent's reasoning trace (for explainability)
  payloadHash: string;     // SHA-256 of the full event payload
}
```

### What Gets Audited

Every event flows through the event bus, but the audit trail filters for significant actions:

| Action Category | Events Captured | Regulatory Basis |
|----------------|-----------------|------------------|
| Session lifecycle | `session:started`, `session:ended` | Traceability |
| Messages | `message:sent`, `message:received` | Transparency, human oversight |
| Commerce actions | All `commerce:*` events | Financial record-keeping |
| Mandate lifecycle | `mandate-presented`, `mandate-signed`, `mandate-rejected` | Consent documentation |
| Agent decisions | `agent:handoff-started`, `agent:human-escalation` | Human oversight |
| Widget interactions | `widget:interaction` (commerce-related only) | Traceability |
| Errors | `error` events | Incident response |

### Tamper Detection

Each audit record includes a `payloadHash` (SHA-256 of the complete event payload). Records are additionally chain-linked: each record includes a hash of the previous record's ID + hash, creating a tamper-evident chain similar to a simplified blockchain. If any record is modified after the fact, the chain breaks.

### Storage

Audit records are written to:
1. **Firestore** — primary durable storage, queryable per session/conversation/user
2. **BigQuery streaming insert** — for aggregation, compliance reporting, and analytics (when BigQuery export is enabled in Phase 3)
3. **Local buffer** — events are buffered locally and flushed in batches to minimize network overhead

### Data Retention

Audit records are retained for the longer of:
- 7 years (financial record-keeping standard)
- Customer-configured retention period
- Regulatory requirement for the deployment jurisdiction

### Privacy

User IDs are pseudonymized (SHA-256 hashed) in audit records. Raw user identity is available only to the customer's own data systems, not stored in the audit trail. This complies with GDPR's data minimization principle while maintaining traceability.

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Audit coverage | 100% of commerce events have corresponding audit records | Reconciliation check |
| Record write latency | P99 <100ms from event to durable write | Firestore latency monitoring |
| Data loss rate | 0% — no events lost under normal operation | Reconciliation between event bus and audit store |
| Chain integrity | 100% of chains pass tamper verification | Periodic integrity checks |
| Storage efficiency | <1 KB per audit record (average) | Storage monitoring |

### Success Criteria

1. An EU compliance auditor can request a complete transaction history for any user session and receive a verified, tamper-evident chain of records within 1 second.
2. Every UCP checkout and AP2 mandate signing has a corresponding audit record that captures what the user consented to, when, and the agent's reasoning.
3. The audit system adds <5ms of latency to event processing (it does not block the event bus).
4. The system detects tampering: if any record is modified, the chain verification fails.

---

## Critical User Journeys

### CUJ 1: EU AI Act Compliance Audit
**Actor:** Compliance officer at a European retailer
**Goal:** Demonstrate that AI shopping agent interactions are fully traceable

1. Regulator requests audit trail for a specific customer complaint
2. Compliance officer queries audit system by session ID or user ID hash
3. System returns a complete chain of records: session start → messages → product recommendations → mandate presentation → mandate signed → checkout → payment → order confirmation
4. Each record includes the agent's reasoning trace (why it recommended that product)
5. Chain integrity verification passes — no records have been altered
6. Compliance officer exports the records as a PDF report

### CUJ 2: Merchant Disputes a Transaction
**Actor:** Merchant support team
**Goal:** Investigate a disputed charge by reviewing the exact checkout flow

1. Customer disputes a $249 charge: "I didn't authorize this purchase"
2. Merchant queries audit trail by order ID
3. System returns: mandate_presented (CheckoutMandate with exact line items + total) → mandate_signed (with timestamp and user confirmation) → payment_completed
4. The CheckoutMandate record includes the exact amount, items, and payment method the user saw when they signed
5. Merchant can demonstrate the customer explicitly consented to the charge

### CUJ 3: Internal Agent Quality Review
**Actor:** GECX operations team
**Goal:** Review agent decision quality for a sample of conversations

1. Operations team queries audit trail for all `agent:handoff-started` events in the last week
2. For each handoff, they pull the full conversation chain
3. Reasoning traces show why the agent decided to hand off
4. Team identifies patterns: agent escalates too early on return requests → feedback to agent training

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Audit trail subscribes to the Event Bus via `onAny()` and filters for auditable events | P0 |
| FR-2 | Each audit record includes all fields defined in the AuditRecord schema | P0 |
| FR-3 | User IDs are pseudonymized (SHA-256) in audit records | P0 |
| FR-4 | Each record includes a `payloadHash` (SHA-256 of event payload) | P0 |
| FR-5 | Records are chain-linked for tamper detection | P0 |
| FR-6 | Records are written to Firestore as primary durable storage | P0 |
| FR-7 | Records are buffered locally and flushed in batches (every 5 seconds or 50 records) | P0 |
| FR-8 | If the network is unavailable, records are buffered in IndexedDB and retried | P0 |
| FR-9 | Audit records include agent `reasoning` trace when available | P1 |
| FR-10 | Chain integrity can be verified by querying a session and checking sequential hashes | P0 |
| FR-11 | Audit records are queryable by sessionId, conversationId, userIdHash, orderId, timeRange | P0 |
| FR-12 | Records are retained for minimum 7 years (configurable) | P1 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Audit logging adds <5ms of latency to event processing | P0 |
| NFR-2 | Audit logging does not block the event bus (async write) | P0 |
| NFR-3 | SHA-256 hashing uses Web Crypto API (not a polyfill) for performance | P0 |
| NFR-4 | Average record size <1 KB | P1 |
| NFR-5 | System handles 1000+ events/second without dropping records | P1 |

---

## Open Questions

1. **Should the audit trail be opt-in or always-on?** EU customers need it; US customers may not. Recommend: always-on for commerce events (legally prudent), opt-in for message-level audit (GDPR data minimization). Configuration in `ChatSDKConfig`.

2. **Who owns the Firestore collection?** If it's in the customer's GCP project, they control retention. If it's in GECX's project, we manage it centrally. Recommend: customer's GCP project for data sovereignty; GECX provides the schema and write logic.

3. **Should the chain-link hashing include all records or only commerce records?** Full chain provides stronger tamper evidence but increases compute. Recommend: chain commerce + mandate records only; other records have standalone hashes.

4. **How do we handle GDPR "right to erasure" requests?** If a user requests data deletion, audit records (which contain pseudonymized data) may need to be retained for financial compliance but the pseudonymization key must be deleted, making re-identification impossible. Need legal review.

---

## Dependencies

- **Event Bus (PRD-002):** Audit trail is a subscriber to `onAny()`
- **AP2 Consent Flows (PRD-010):** Mandate events must include complete mandate data
- **Commerce Engine (PRD-009):** Commerce events must include session and amount data
- **Firestore / BigQuery:** Backend infrastructure

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Audit schema finalized + legal review | April 2026 Week 2 | Record schema and retention policy approved |
| Event Bus subscriber implemented | May 2026 | Audit logger captures all events with hashing |
| Firestore write + batching | May 2026 Week 3 | Durable storage with offline buffering |
| Chain integrity verification | June 2026 | Tamper detection passes integration tests |
| Compliance review | July 2026 | EU AI Act compliance verified by legal team |
| GA with SDK v2 | July 2026 | Shipped with Phase 1 commerce features |
