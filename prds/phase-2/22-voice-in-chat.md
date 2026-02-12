# PRD-022: Voice-in-Chat

**Phase:** 2 — "Make It Intelligent" | **Priority:** P1 | **Quarter:** Q4 2026
**Pillar:** Multimodal | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The current SDK supports a voice-only mode or a text-only mode, but not both simultaneously. Users cannot send a voice message within a text chat, and there is no transcription visible in the thread. Competitors — Salesforce Agentforce Voice, Shopify Sidekick, and Amazon Rufus — all support inline voice within text conversations.

Voice-in-Chat makes voice a first-class message type within text conversations. Users can press-and-hold to record a voice message, see the automatic transcription, and receive agent responses in their preferred modality (text or voice).

---

## What Are We Building

### Voice Message Recording

A press-and-hold microphone button in the input bar:
- **Press and hold:** Start recording (visual waveform indicator)
- **Release:** Stop recording → audio uploaded → transcription begins
- **Swipe away:** Cancel recording

### Voice Message Display

```
┌──────────────────────────────────────┐
│ You (voice message)                   │
│ ▶ ═══════════●═══════  0:04 / 0:08  │  ← playable audio
│ "I'm looking for a birthday gift     │  ← auto-transcription
│  for my sister"                       │
├──────────────────────────────────────┤
│ 🛒 Shopping Assistant                │
│ What kinds of things does your       │  ← text response (default)
│ sister enjoy?                        │
│ 🔊 [Listen]                          │  ← optional voice response
└──────────────────────────────────────┘
```

### Response Modality Preference

Users can set their preferred response modality:
- **Text only (default):** Agent responds with text
- **Voice preferred:** Agent responds with synthesized voice + text transcription
- **Auto:** Agent matches the user's modality (voice in → voice out)

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Voice message adoption | >5% of sessions include voice messages | Message analytics |
| Transcription accuracy | >95% (WER <5%) | Transcription quality monitoring |
| Voice-to-text latency | <2 seconds from recording end to transcription display | Performance monitoring |

### Success Criteria

1. A user records a voice message, sees accurate transcription within 2 seconds, and receives a relevant agent response.
2. Voice messages are fully accessible — the transcription serves as the accessible text for screen reader users.
3. Voice recording works on mobile (iOS Safari, Android Chrome) and desktop.

---

## Critical User Journeys

### CUJ 1: Hands-Free Shopping
**Actor:** User cooking in the kitchen, hands dirty
**Goal:** Add groceries to cart via voice

1. User presses and holds microphone button
2. "Add eggs, milk, and bread to my cart"
3. Releases → transcription appears → agent processes
4. Agent: "I've added a dozen eggs ($3.99), whole milk ($4.49), and wheat bread ($2.99) to your Kroger cart."

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Press-and-hold microphone button records audio | P0 |
| FR-2 | Visual waveform indicator during recording | P0 |
| FR-3 | Swipe-to-cancel recording gesture | P1 |
| FR-4 | Audio uploaded to speech-to-text API on release | P0 |
| FR-5 | Transcription displayed in the message alongside playable audio | P0 |
| FR-6 | Agent can respond with synthesized speech (optional, configurable) | P1 |
| FR-7 | Response modality preference setting (text, voice, auto) | P1 |
| FR-8 | Microphone permission request with clear explanation | P0 |
| FR-9 | Voice messages appear in conversation history with transcription | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Voice module is lazy-loaded (~12 KB gzipped) | P0 |
| NFR-2 | Transcription latency <2 seconds for messages under 30 seconds | P0 |
| NFR-3 | Audio compressed before upload (Opus codec, <100 KB/minute) | P0 |
| NFR-4 | Works on iOS Safari, Android Chrome, desktop Chrome/Firefox | P0 |

---

## Open Questions

1. **Maximum recording length.** Recommend: 2 minutes. Longer messages are rare in chat context and increase transcription cost.
2. **Background noise handling.** Should we add noise suppression? Recommend: use the browser's built-in echo cancellation; server-side noise suppression via the speech API.
3. **Language detection.** Should voice messages auto-detect language? Recommend: use the SDK's configured language as the transcription hint; allow override.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** AudioBlock message type
- **Accessibility (PRD-005):** Transcription is the accessible text
- **Mobile Design (PRD-008):** Touch-optimized recording gesture
- **Google Cloud Speech-to-Text API:** Transcription backend
- **Google Cloud Text-to-Speech API:** Agent voice responses

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Audio recording + upload | October 2026 | Press-and-hold, waveform, compression |
| Transcription display | November 2026 | STT integration, inline display |
| Voice response (TTS) | November 2026 Week 3 | Agent speech synthesis |
| GA | December 2026 | Shipped with Phase 2 |
