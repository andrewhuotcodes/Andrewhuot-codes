# PRD-026: Native Mobile SDKs (iOS + Android)

**Phase:** 3 — "Make It Scale" | **Priority:** P1 | **Quarter:** Q1-Q2 2027
**Pillar:** Platform | **Status:** Draft
**Author:** Chat SDK Product Lead | **Last Updated:** February 2026

---

## Introduction

The Chat SDK is web-only. Retail partners like Kroger, Papa Johns, and Lowe's all have native mobile apps where customers prefer to shop. Embedding a WebView-wrapped web widget in a native app produces a second-class experience — platform-inconsistent interactions, no access to native APIs (biometrics, haptics, push notifications), and performance overhead.

Native Mobile SDKs for iOS and Android provide first-class, platform-native chat experiences that integrate seamlessly with native app navigation, design systems, and capabilities.

---

## What Are We Building

### iOS SDK (`GECXChatSDK` — Swift Package)

- SwiftUI and UIKit components (`ChatView`, `ChatBubble`, `ChatTriggerButton`)
- Native rendering of all widget types using UIKit/SwiftUI
- Platform integration: Face ID for payment auth, haptic feedback, push notifications for agent responses
- Apple Pay integration (in addition to Google Pay)
- VoiceOver accessibility (native, not ARIA-based)

### Android SDK (`gecx-chat-sdk` — Kotlin library)

- Jetpack Compose and View-based components (`ChatComposable`, `ChatView`, `ChatTriggerView`)
- Material Design 3 native widgets
- Platform integration: biometric auth, haptic feedback, Firebase push notifications
- Google Pay native integration
- TalkBack accessibility

### Shared Architecture

Both SDKs share the same:
- Event bus contract (same event types and payloads)
- Commerce engine logic (same UCP/ACP state machines)
- Widget data schemas (same JSON structures)
- Backend API (same Conversational Agents Runtime endpoints)

Widget renderers are platform-native — not shared. A `product_carousel` on iOS uses a `UICollectionView` with horizontal scrolling; on Android it uses a `RecyclerView` with `SnapHelper`.

### API Parity

```swift
// iOS (Swift)
let sdk = GECXChatSDK(config: ChatSDKConfig(
    deploymentId: "projects/my-project/...",
    language: "en",
    auth: .tokenBroker(endpoint: "/api/auth/token")
))

sdk.open()
sdk.setContext(key: "product_id", value: "SKU-123")
sdk.on(.commercePaymentCompleted) { event in
    print("Order: \(event.payload.orderId)")
}
```

```kotlin
// Android (Kotlin)
val sdk = GECXChatSDK(ChatSDKConfig(
    deploymentId = "projects/my-project/...",
    language = "en",
    auth = AuthConfig.TokenBroker(endpoint = "/api/auth/token")
))

sdk.open()
sdk.setContext("product_id", "SKU-123")
sdk.on(ChatEvent.CommercePaymentCompleted) { event ->
    println("Order: ${event.payload.orderId}")
}
```

---

## What Does Success Look Like

### Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| SDK installs (apps using the SDK) | 100+ apps within 6 months of GA | SDK distribution tracking |
| Native SDK checkout conversion | >10% higher than WebView equivalent | A/B testing |
| App store rating impact | No negative impact on partner app ratings | App store monitoring |
| Crash-free rate | >99.9% | Crashlytics/Sentry |

### Success Criteria

1. Kroger's iOS and Android apps integrate the native SDK and the chat experience feels indistinguishable from a first-party feature.
2. Native SDKs achieve API parity with the web SDK for core features (lifecycle, messaging, events, commerce).
3. Both SDKs pass platform accessibility audits (VoiceOver on iOS, TalkBack on Android).
4. Beta SDKs available by Q1 2027; GA by Q2 2027.

---

## Critical User Journeys

### CUJ 1: Native App Shopping
**Actor:** Kroger app user on iPhone
**Goal:** Buy groceries through chat in the native app

1. User taps chat icon in Kroger's tab bar → native chat view slides up
2. "Show me deals on organic produce" → product carousel with native UICollectionView
3. Adds items → native cart view with haptic feedback on add
4. Checkout → Face ID for Apple Pay → order confirmed
5. Push notification 2 hours later: "Your Kroger order is ready for pickup"

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | iOS SDK with SwiftUI and UIKit components | P0 |
| FR-2 | Android SDK with Jetpack Compose and View components | P0 |
| FR-3 | API parity with web SDK for core features | P0 |
| FR-4 | Native widget rendering (not WebView) for all built-in widgets | P0 |
| FR-5 | Platform biometric auth for payments (Face ID, fingerprint) | P0 |
| FR-6 | Push notification support for agent responses | P1 |
| FR-7 | Custom widget support via platform-native rendering callbacks | P1 |
| FR-8 | Apple Pay integration (iOS) | P1 |
| FR-9 | VoiceOver (iOS) and TalkBack (Android) accessibility | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | SDK binary size: <5 MB per platform | P0 |
| NFR-2 | Cold start initialization: <500ms | P0 |
| NFR-3 | Crash-free rate: >99.9% | P0 |
| NFR-4 | Minimum OS: iOS 16+, Android API 26+ (Android 8.0) | P0 |

---

## Open Questions

1. **Flutter SDK.** Several Google properties use Flutter. Should we ship a Flutter SDK? Recommend: evaluate demand after iOS/Android native SDKs ship.
2. **Widget rendering strategy.** Should custom widgets use a platform WebView, or must they be fully native? Recommend: built-in widgets are native; custom widgets render in a constrained WebView with the same data schemas.
3. **SDK distribution.** Swift Package Manager + CocoaPods for iOS; Maven Central for Android? Recommend: SPM (primary) + CocoaPods (legacy) for iOS; Maven Central for Android.

---

## Dependencies

- **SDK v2 Core API (PRD-001):** API parity target
- **Commerce Engine (PRD-009):** Same UCP state machine
- **Widget Registry (PRD-003):** Same widget data schemas
- **GECX backend:** Same REST/WebSocket endpoints

---

## Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Platform architecture defined | November 2026 | Shared vs. native module boundaries |
| iOS alpha | January 2027 | Core features working in SwiftUI |
| Android alpha | January 2027 | Core features working in Compose |
| Beta (partner preview) | March 2027 | Available to 5 launch partners |
| GA | June 2027 | Published to SPM + Maven Central |
