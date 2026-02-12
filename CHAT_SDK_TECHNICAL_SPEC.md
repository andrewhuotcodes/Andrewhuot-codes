# Chat SDK v2: Technical Specification
## Code-Ready Architecture & Interface Definitions

*This document provides implementable interface definitions, data schemas, and architectural patterns for the Chat SDK v2. It is intended to be directly translatable into TypeScript source code.*

---

## 1. Module Architecture

```
@gecx/chat-sdk/
├── core/                    # ~30 KB gzipped — always loaded
│   ├── event-bus.ts         # Typed event system with audit logging
│   ├── sdk.ts               # Main ChatSDK class and public API
│   ├── session.ts           # Session management and persistence
│   ├── config.ts            # Configuration and initialization
│   └── types.ts             # Core type definitions
│
├── renderer/                # ~15 KB gzipped — always loaded
│   ├── message-renderer.ts  # Streaming message renderer
│   ├── widget-registry.ts   # Widget registration and resolution
│   ├── widget-host.ts       # Sandboxed widget container
│   └── theme.ts             # CSS custom property engine
│
├── a11y/                    # ~8 KB gzipped — always loaded
│   ├── keyboard.ts          # Keyboard navigation manager
│   ├── focus.ts             # Focus trap and restoration
│   ├── announcer.ts         # Screen reader live region management
│   └── aria.ts              # ARIA attribute helpers
│
├── commerce/                # ~25 KB gzipped — lazy loaded on first commerce event
│   ├── cart.ts              # Cross-merchant cart state machine
│   ├── checkout.ts          # UCP checkout session manager
│   ├── embedded-checkout.ts # Embedded checkout bridge (JSON-RPC 2.0)
│   ├── mandate.ts           # AP2 mandate renderer and signer
│   ├── acp-adapter.ts       # ACP protocol compatibility layer
│   └── payments.ts          # Google Pay and payment handler integration
│
├── widgets/                 # ~3-8 KB each — lazy loaded per widget type
│   ├── product-carousel.ts
│   ├── product-details.ts
│   ├── product-comparison.ts
│   ├── order-summary.ts
│   ├── quick-actions.ts
│   ├── checkout-flow.ts
│   ├── cart-view.ts
│   ├── fulfillment-picker.ts
│   ├── form.ts
│   ├── calendar.ts
│   ├── map-location.ts
│   └── rating-review.ts
│
├── streaming/               # ~6 KB gzipped — lazy loaded on first stream
│   ├── stream-processor.ts  # Block-level stream parser
│   ├── text-streamer.ts     # Token-by-token text renderer
│   └── widget-streamer.ts   # Progressive widget data accumulator
│
├── analytics/               # ~4 KB gzipped — lazy loaded
│   ├── collector.ts         # Event aggregation and batching
│   ├── funnel.ts            # Commerce funnel state machine
│   └── export.ts            # BigQuery / webhook export
│
├── voice/                   # ~12 KB gzipped — lazy loaded
│   ├── recorder.ts          # Audio capture
│   ├── transcription.ts     # Speech-to-text integration
│   └── playback.ts          # Text-to-speech for agent responses
│
├── react/                   # Separate package: @gecx/chat-sdk-react
│   ├── ChatProvider.tsx
│   ├── ChatWidget.tsx
│   ├── ChatTrigger.tsx
│   └── hooks.ts             # useChatSDK, useConversation, useCommerce
│
└── web-components/          # Separate package: @gecx/chat-sdk-elements
    ├── chat-messenger.ts    # <gecx-chat> custom element (v2)
    ├── chat-bubble.ts       # <gecx-chat-bubble>
    └── chat-container.ts    # <gecx-chat-container>
```

---

## 2. Core Type Definitions

```typescript
// ============================================================
// core/types.ts — Foundation types used across all modules
// ============================================================

// --- Identity ---

export interface UserIdentity {
  /** Unique user identifier */
  userId: string;
  /** Display name shown in chat */
  displayName?: string;
  /** Email for account linking */
  email?: string;
  /** Avatar URL */
  avatarUrl?: string;
  /** OAuth access token for authenticated operations */
  accessToken?: string;
  /** Arbitrary user attributes for agent context */
  attributes?: Record<string, string | number | boolean>;
}

export interface AgentIdentity {
  /** Agent identifier within the GECX platform */
  agentId: string;
  /** Display name shown in chat */
  displayName: string;
  /** Avatar URL */
  avatarUrl?: string;
  /** Agent type for multi-agent threads */
  role: 'shopping' | 'service' | 'food_ordering' | 'custom';
  /** Whether this agent has been verified via KYA */
  verified: boolean;
}

// --- Messages ---

export type MessageRole = 'user' | 'agent' | 'system';

export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  agent?: AgentIdentity;
  timestamp: number;
  blocks: MessageBlock[];
  metadata?: Record<string, unknown>;
}

export type MessageBlock =
  | TextBlock
  | WidgetBlock
  | ImageBlock
  | AudioBlock
  | ActionBlock;

export interface TextBlock {
  type: 'text';
  content: string;
  /** BCP 47 language tag if different from conversation default */
  lang?: string;
}

export interface WidgetBlock {
  type: 'widget';
  widgetType: string;
  data: unknown;
  /** Unique ID for this widget instance */
  instanceId: string;
}

export interface ImageBlock {
  type: 'image';
  url: string;
  alt: string;
  width?: number;
  height?: number;
}

export interface AudioBlock {
  type: 'audio';
  url: string;
  duration: number;
  transcription?: string;
}

export interface ActionBlock {
  type: 'action';
  actions: ActionButton[];
}

export interface ActionButton {
  id: string;
  label: string;
  /** Visual style hint */
  style: 'primary' | 'secondary' | 'danger';
  /** Payload sent back to agent when clicked */
  payload: unknown;
  /** Whether this action has been used (one-time actions) */
  disabled?: boolean;
}

// --- Configuration ---

export interface ChatSDKConfig {
  /** GECX deployment resource path */
  deploymentId: string;
  /** BCP 47 language code */
  language: string;
  /** Authentication configuration */
  auth: AuthConfig;
  /** Visual theme overrides */
  theme?: Partial<ThemeTokens>;
  /** Initial display mode */
  displayMode: 'floating' | 'side-panel' | 'inline';
  /** Maximum input length (-1 for unlimited) */
  maxInputLength: number;
  /** Enable conversation history persistence */
  persistHistory: boolean;
  /** Enable debug console */
  debug: boolean;
  /** Content Security Policy nonce for inline styles */
  cspNonce?: string;
  /** Sandbox mode for widget rendering */
  sandboxMode: 'shadow-dom' | 'iframe';
  /** Commerce engine configuration */
  commerce?: CommerceConfig;
  /** Proactive engagement rules */
  proactive?: ProactiveConfig;
  /** Accessibility overrides */
  a11y?: AccessibilityConfig;
}

export type AuthConfig =
  | { type: 'token-broker'; endpoint: string; enableRecaptcha?: boolean }
  | { type: 'oauth2'; clientId: string }
  | { type: 'custom'; getToken: () => Promise<string> }
  | { type: 'anonymous' };

export interface CommerceConfig {
  /** Enable UCP checkout capabilities */
  enableUCP: boolean;
  /** Enable ACP compatibility layer */
  enableACP: boolean;
  /** Google Pay configuration */
  googlePay?: {
    merchantId: string;
    merchantName: string;
    environment: 'TEST' | 'PRODUCTION';
  };
  /** Supported payment methods beyond Google Pay */
  paymentMethods?: string[];
  /** Default currency for display */
  defaultCurrency: string;
}

export interface AccessibilityConfig {
  /** Override the widget's accessible label */
  widgetLabel?: string;
  /** Enable high contrast mode */
  highContrast?: boolean;
  /** Reduce motion for animations */
  reduceMotion?: boolean;
  /** Custom keyboard shortcuts */
  shortcuts?: Record<string, string>;
}
```

---

## 3. Event Bus Specification

```typescript
// ============================================================
// core/event-bus.ts — Typed event system
// ============================================================

// --- Event Type Map ---
// Every event has a typed payload. Adding a new event means adding
// an entry here — the compiler enforces that all emitters and
// subscribers agree on the payload shape.

export interface ChatEventMap {
  // Lifecycle
  'sdk:initialized': { config: ChatSDKConfig };
  'sdk:destroyed': {};

  // Session
  'session:started': { sessionId: string; conversationId: string; isRestored: boolean };
  'session:restored': { sessionId: string; messageCount: number };
  'session:ended': { sessionId: string; reason: 'user' | 'timeout' | 'error' };

  // Messages
  'message:sending': { text: string; metadata?: Record<string, unknown> };
  'message:sent': { message: Message };
  'message:received': { message: Message };
  'message:stream-start': { messageId: string; agent: AgentIdentity };
  'message:stream-delta': { messageId: string; block: StreamBlock };
  'message:stream-end': { messageId: string };

  // Widgets
  'widget:rendered': { widgetType: string; instanceId: string; renderTimeMs: number };
  'widget:interaction': { widgetType: string; instanceId: string; action: string; payload: unknown };
  'widget:error': { widgetType: string; instanceId: string; error: Error };

  // Typing
  'typing:user-start': {};
  'typing:user-stop': {};
  'typing:agent-start': { agent: AgentIdentity };
  'typing:agent-stop': { agent: AgentIdentity };

  // Commerce
  'commerce:cart-updated': { cart: CartState };
  'commerce:checkout-started': { sessionId: string; merchant: string };
  'commerce:checkout-state-changed': { sessionId: string; from: string; to: string };
  'commerce:escalation-started': { sessionId: string; continueUrl: string };
  'commerce:escalation-completed': { sessionId: string; result: 'success' | 'cancelled' };
  'commerce:mandate-presented': { type: 'intent' | 'checkout' | 'payment'; mandateId: string };
  'commerce:mandate-signed': { mandateId: string; signature: string };
  'commerce:mandate-rejected': { mandateId: string; reason?: string };
  'commerce:payment-started': { method: string; amount: Money };
  'commerce:payment-completed': { orderId: string; amount: Money };
  'commerce:payment-failed': { error: CommerceError };

  // Agent handoffs
  'agent:handoff-started': { from: AgentIdentity; to: AgentIdentity; reason?: string };
  'agent:handoff-completed': { agent: AgentIdentity };
  'agent:human-escalation': { queuePosition?: number };

  // Proactive engagement
  'proactive:triggered': { ruleId: string; triggerType: string };
  'proactive:accepted': { ruleId: string };
  'proactive:dismissed': { ruleId: string };

  // Display
  'display:opened': { trigger: 'user' | 'programmatic' | 'proactive' };
  'display:closed': { trigger: 'user' | 'programmatic' };
  'display:minimized': {};
  'display:maximized': {};

  // Errors
  'error': { code: string; message: string; details?: unknown };
}

// --- Event Bus Implementation Contract ---

export interface EventBus {
  /** Subscribe to a specific event type */
  on<K extends keyof ChatEventMap>(
    type: K,
    handler: (event: ChatEvent<ChatEventMap[K]>) => void
  ): () => void;  // returns unsubscribe function

  /** Subscribe to all events (for audit logging, analytics) */
  onAny(
    handler: (event: ChatEvent<unknown>) => void
  ): () => void;

  /** Emit an event */
  emit<K extends keyof ChatEventMap>(
    type: K,
    payload: ChatEventMap[K]
  ): void;

  /** One-time subscription */
  once<K extends keyof ChatEventMap>(
    type: K,
    handler: (event: ChatEvent<ChatEventMap[K]>) => void
  ): () => void;
}

export interface ChatEvent<T> {
  /** Globally unique event ID (UUIDv7 for time-ordering) */
  id: string;
  /** Event type from ChatEventMap */
  type: string;
  /** Unix timestamp in milliseconds */
  timestamp: number;
  /** Event source */
  source: 'user' | 'agent' | 'system' | 'widget' | 'commerce';
  /** Session context */
  sessionId: string;
  conversationId: string;
  /** Typed payload */
  payload: T;
}
```

---

## 4. Widget Registry Specification

```typescript
// ============================================================
// renderer/widget-registry.ts
// ============================================================

export interface WidgetDefinition<TData = unknown, TAction = unknown> {
  /** Unique widget type identifier (e.g., 'product_comparison') */
  type: string;
  /** Semantic version */
  version: string;
  /** JSON Schema for validating incoming data */
  schema: JSONSchema7;
  /**
   * Render function. Receives a container element, validated data, and context.
   * May return a cleanup function called when the widget is removed from the DOM.
   * May be async for lazy-loaded widget implementations.
   */
  render: (
    container: HTMLElement,
    data: TData,
    context: WidgetContext
  ) => void | (() => void) | Promise<void | (() => void)>;
  /**
   * Optional: handle user interactions within the widget.
   * If not provided, the widget must call context.emit() directly.
   */
  onAction?: (action: TAction, context: WidgetContext) => void;
  /**
   * REQUIRED: Accessibility metadata.
   * The registry will warn on registration if this is missing.
   */
  accessibility: WidgetAccessibility<TData>;
  /**
   * Optional: whether this widget supports progressive/partial rendering
   * during streaming. If true, render() may be called multiple times
   * with increasingly complete data.
   */
  supportsStreaming?: boolean;
  /**
   * Optional: estimated render height in pixels for skeleton placeholder.
   * Used to minimize layout shift during lazy loading.
   */
  estimatedHeight?: number | ((data: TData) => number);
}

export interface WidgetAccessibility<TData = unknown> {
  /** ARIA role for the widget's root element */
  role: string;
  /** Accessible label — static string or function of data */
  label: string | ((data: TData) => string);
  /**
   * Text announced by screen reader when the widget first renders.
   * Should describe what the widget shows, not how to interact with it.
   */
  announceOnRender?: string | ((data: TData) => string);
  /**
   * Whether the widget manages its own focus internally.
   * If true, the keyboard navigation manager delegates to the widget.
   * If false, the widget's interactive elements participate in the
   * chat thread's tab order.
   */
  managesFocus?: boolean;
}

export interface WidgetContext {
  /** Current theme tokens for consistent styling */
  theme: ThemeTokens;
  /** BCP 47 locale (e.g., 'en-US', 'ja-JP') */
  locale: string;
  /** Text direction */
  direction: 'ltr' | 'rtl';
  /** Current viewport category */
  viewport: 'mobile' | 'tablet' | 'desktop';
  /** Viewport width in pixels */
  viewportWidth: number;
  /** Send an interaction event back to the event bus */
  emit: (action: string, payload: unknown) => void;
  /** Request the commerce engine (lazy loaded) */
  getCommerce: () => Promise<CommerceEngine>;
  /** Get localized string */
  t: (key: string, params?: Record<string, string | number>) => string;
  /** CSP nonce for inline styles/scripts */
  cspNonce?: string;
}

// --- Widget Registry API ---

export interface WidgetRegistry {
  /** Register a widget definition. Overwrites existing registration for same type. */
  register<TData, TAction>(definition: WidgetDefinition<TData, TAction>): void;

  /** Unregister a widget type */
  unregister(type: string): void;

  /** Check if a widget type is registered */
  has(type: string): boolean;

  /** Get all registered widget types */
  types(): string[];

  /** Resolve and render a widget. Returns cleanup function. */
  render(
    type: string,
    data: unknown,
    container: HTMLElement,
    context: WidgetContext
  ): Promise<(() => void) | void>;

  /**
   * Set the fallback renderer for unregistered widget types.
   * This is where the Generative UI pipeline plugs in.
   */
  setFallback(
    renderer: (type: string, data: unknown, container: HTMLElement, context: WidgetContext) => Promise<void>
  ): void;
}
```

---

## 5. Commerce Engine Specification

```typescript
// ============================================================
// commerce/types.ts — Commerce data structures
// ============================================================

export interface Money {
  amount: number;          // in minor units (cents)
  currency: string;        // ISO 4217 (e.g., 'USD')
}

export interface LineItem {
  id: string;
  productId: string;
  name: string;
  description?: string;
  imageUrl?: string;
  quantity: number;
  unitPrice: Money;
  totalPrice: Money;
  attributes?: Record<string, string>;  // size, color, etc.
}

export interface Discount {
  code?: string;
  description: string;
  amount: Money;
  type: 'percentage' | 'fixed' | 'loyalty';
}

export interface FulfillmentOption {
  id: string;
  type: 'shipping' | 'pickup' | 'local_delivery';
  label: string;
  cost: Money;
  estimatedDelivery?: string;      // ISO 8601 date or date range
  deliveryWindows?: DeliveryWindow[];
}

export interface DeliveryWindow {
  id: string;
  date: string;         // ISO 8601 date
  startTime: string;    // HH:mm
  endTime: string;      // HH:mm
  cost: Money;
}

// --- Cart State ---

export interface CartState {
  merchants: MerchantCart[];
  totalItems: number;
  estimatedTotal: Money;
  lastUpdated: number;
}

export interface MerchantCart {
  merchantId: string;
  merchantName: string;
  merchantUrl: string;
  items: LineItem[];
  subtotal: Money;
  discounts: Discount[];
  tax?: Money;
  fulfillment?: FulfillmentOption;
  checkoutSessionId?: string;
}

// --- Checkout State Machine ---

export type CheckoutStatus =
  | 'idle'
  | 'cart_open'
  | 'checkout_initiated'
  | 'incomplete'
  | 'requires_escalation'
  | 'ready_for_complete'
  | 'processing_payment'
  | 'completed'
  | 'error';

export interface CheckoutSession {
  sessionId: string;
  merchantId: string;
  status: CheckoutStatus;
  cart: MerchantCart;
  fulfillment?: FulfillmentOption;
  paymentMethod?: PaymentMethod;
  totals: CheckoutTotals;
  mandates: MandateState;
  /** For requires_escalation: URL to merchant's embedded checkout */
  continueUrl?: string;
  /** Missing fields that must be provided before checkout can complete */
  missingFields?: string[];
  createdAt: number;
  updatedAt: number;
}

export interface CheckoutTotals {
  subtotal: Money;
  discounts: Money;
  tax: Money;
  shipping: Money;
  total: Money;
}

export interface PaymentMethod {
  type: 'google_pay' | 'card' | 'paypal' | 'custom';
  displayName: string;
  last4?: string;
  expiryDate?: string;
}

// --- AP2 Mandates ---

export type MandateType = 'intent' | 'checkout' | 'payment';

export interface Mandate {
  id: string;
  type: MandateType;
  status: 'pending' | 'signed' | 'rejected' | 'expired';
  /** Human-readable description of what the user is authorizing */
  description: string;
  /** Structured data specific to the mandate type */
  data: IntentMandateData | CheckoutMandateData | PaymentMandateData;
  /** ISO 8601 expiration time */
  expiresAt: string;
  /** Cryptographic signature after user signs */
  signature?: string;
}

export interface IntentMandateData {
  /** User's original request */
  userIntent: string;
  /** Scope of authority granted to the agent */
  authorizedActions: string[];
  /** Budget limit if applicable */
  budgetLimit?: Money;
}

export interface CheckoutMandateData {
  /** Line items the user is agreeing to purchase */
  items: LineItem[];
  /** Price breakdown */
  totals: CheckoutTotals;
  /** Merchant's cryptographic signature on the offer */
  merchantSignature: string;
}

export interface PaymentMandateData {
  /** Payment method being authorized */
  paymentMethod: PaymentMethod;
  /** Exact amount authorized */
  amount: Money;
  /** Hash of the checkout session this payment is scoped to */
  checkoutHash: string;
}

export interface MandateState {
  intent?: Mandate;
  checkout?: Mandate;
  payment?: Mandate;
}

// --- Commerce Engine API ---

export interface CommerceEngine {
  // Cart operations
  getCart(): CartState;
  addToCart(merchantId: string, item: LineItem): void;
  removeFromCart(merchantId: string, itemId: string): void;
  updateQuantity(merchantId: string, itemId: string, quantity: number): void;
  clearCart(merchantId?: string): void;

  // Checkout operations
  initiateCheckout(merchantId: string): Promise<CheckoutSession>;
  updateCheckout(sessionId: string, updates: Partial<CheckoutSession>): Promise<CheckoutSession>;
  applyDiscount(sessionId: string, code: string): Promise<CheckoutSession>;
  selectFulfillment(sessionId: string, optionId: string): Promise<CheckoutSession>;
  selectPaymentMethod(sessionId: string, method: PaymentMethod): Promise<CheckoutSession>;
  completeCheckout(sessionId: string): Promise<OrderConfirmation>;
  cancelCheckout(sessionId: string): Promise<void>;

  // Mandate operations
  presentMandate(mandate: Mandate): Promise<'signed' | 'rejected'>;
  getMandate(mandateId: string): Mandate | undefined;

  // Embedded checkout bridge
  openEmbeddedCheckout(continueUrl: string, sessionId: string): Promise<EmbeddedCheckoutResult>;

  // State
  getCheckoutSession(sessionId: string): CheckoutSession | undefined;
  getActiveCheckouts(): CheckoutSession[];

  // Subscriptions
  onCartChange(handler: (cart: CartState) => void): () => void;
  onCheckoutChange(sessionId: string, handler: (session: CheckoutSession) => void): () => void;
}

export interface OrderConfirmation {
  orderId: string;
  merchantOrderId: string;
  items: LineItem[];
  totals: CheckoutTotals;
  fulfillment: FulfillmentOption;
  paymentMethod: PaymentMethod;
  estimatedDelivery?: string;
  trackingUrl?: string;
  timestamp: number;
}

export interface EmbeddedCheckoutResult {
  status: 'completed' | 'cancelled' | 'error';
  orderId?: string;
  error?: string;
}
```

---

## 6. Streaming Renderer Specification

```typescript
// ============================================================
// streaming/stream-processor.ts
// ============================================================

export type StreamBlock =
  | { type: 'text_delta'; content: string }
  | { type: 'text_end' }
  | { type: 'widget_start'; widget_type: string; instance_id: string }
  | { type: 'widget_data_delta'; data: string }
  | { type: 'widget_end' }
  | { type: 'action_block'; actions: ActionButton[] }
  | { type: 'thinking_start' }
  | { type: 'thinking_delta'; content: string }
  | { type: 'thinking_end' }
  | { type: 'error'; code: string; message: string };

export interface StreamingRendererConfig {
  /** Container element for the streaming message */
  container: HTMLElement;
  /** Widget registry for resolving widget blocks */
  widgetRegistry: WidgetRegistry;
  /** Widget rendering context */
  widgetContext: WidgetContext;
  /** Callback when the full message is assembled */
  onComplete: (message: Message) => void;
  /** Callback for screen reader announcements */
  onAnnounce: (text: string) => void;
  /** Whether to show thinking/reasoning blocks */
  showThinking: boolean;
}

export interface StreamingRenderer {
  /** Process a single stream block */
  processBlock(block: StreamBlock): void;
  /** Signal end of stream */
  end(): void;
  /** Abort the current stream (e.g., user navigated away) */
  abort(): void;
  /** Get the assembled message so far */
  getCurrentMessage(): Partial<Message>;
}

// --- Accessible Stream Announcer ---

export interface StreamAnnouncerConfig {
  /** The aria-live region element */
  liveRegion: HTMLElement;
  /** Debounce time before announcing buffered text */
  debounceMs: number;   // default: 500
  /** Announce on sentence boundaries */
  announceOnSentence: boolean;  // default: true
}
```

---

## 7. Public SDK API

```typescript
// ============================================================
// core/sdk.ts — The main public API
// ============================================================

export interface ChatSDK {
  // --- Lifecycle ---

  /** Initialize the SDK with configuration. Must be called before any other method. */
  init(config: ChatSDKConfig): Promise<void>;
  /** Open the chat widget */
  open(): void;
  /** Close the chat widget */
  close(): void;
  /** Minimize to the floating bubble */
  minimize(): void;
  /** Destroy the SDK instance and clean up all resources */
  destroy(): void;
  /** Reset the conversation (clears history, starts new session) */
  reset(): Promise<void>;
  /** Check if the SDK is initialized */
  readonly initialized: boolean;
  /** Check if the widget is currently open */
  readonly isOpen: boolean;

  // --- Messaging ---

  /** Send a text message as the user */
  sendMessage(text: string, metadata?: Record<string, unknown>): Promise<Message>;
  /** Send a structured action (e.g., button click, widget interaction) */
  sendAction(actionId: string, payload: unknown): Promise<void>;
  /** Render a custom text message in the chat (as if from agent) */
  renderText(text: string): void;
  /** Render a widget in the chat (as if from agent) */
  renderWidget(widgetType: string, data: unknown): void;

  // --- Context ---

  /** Set a context value available to the agent */
  setContext(key: string, value: unknown): void;
  /** Get a context value */
  getContext(key: string): unknown;
  /** Set the user's identity */
  setUserIdentity(identity: UserIdentity): void;
  /** Get the current user identity */
  getUserIdentity(): UserIdentity | null;
  /** Change the conversation language */
  setLanguage(languageCode: string): void;

  // --- Session ---

  /** Get the current session ID */
  getSessionId(): string | null;
  /** Get the current conversation ID */
  getConversationId(): string | null;
  /** Get conversation history */
  getHistory(): Promise<Message[]>;
  /** Restore a previous session */
  restoreSession(sessionId: string): Promise<void>;
  /** Clear conversation history */
  clearHistory(): Promise<void>;

  // --- Commerce ---

  /** Get the commerce engine (lazy loaded) */
  getCommerce(): Promise<CommerceEngine>;

  // --- Events ---

  /** Subscribe to a typed event */
  on<K extends keyof ChatEventMap>(
    type: K,
    handler: (event: ChatEvent<ChatEventMap[K]>) => void
  ): () => void;
  /** Subscribe to all events */
  onAny(handler: (event: ChatEvent<unknown>) => void): () => void;
  /** One-time event subscription */
  once<K extends keyof ChatEventMap>(
    type: K,
    handler: (event: ChatEvent<ChatEventMap[K]>) => void
  ): () => void;

  // --- Widgets ---

  /** Register a custom widget type */
  registerWidget<TData, TAction>(definition: WidgetDefinition<TData, TAction>): void;
  /** Unregister a widget type */
  unregisterWidget(type: string): void;

  // --- Plugins ---

  /** Register a plugin */
  registerPlugin(plugin: ChatPlugin): void;

  // --- Analytics ---

  /** Track a custom analytics event */
  trackEvent(name: string, properties?: Record<string, unknown>): void;

  // --- Deep Linking ---

  /** Open the widget with a pre-populated message (e.g., from URL params) */
  openWithMessage(text: string): void;
  /** Open the widget with a specific context (e.g., from product page) */
  openWithContext(context: Record<string, unknown>): void;
}

// --- Plugin Interface ---

export interface ChatPlugin {
  /** Unique plugin identifier */
  name: string;
  /** Plugin version */
  version: string;
  /** Called when the plugin is registered */
  install(sdk: ChatSDK): void;
  /** Called when the SDK is destroyed */
  uninstall?(): void;
}
```

---

## 8. React SDK Specification

```typescript
// ============================================================
// react/hooks.ts — React integration
// ============================================================

// --- Provider ---

export interface ChatProviderProps {
  config: ChatSDKConfig;
  children: React.ReactNode;
  /** Called when SDK initialization completes */
  onReady?: (sdk: ChatSDK) => void;
  /** Called on initialization error */
  onError?: (error: Error) => void;
}

// <ChatProvider config={config}>{children}</ChatProvider>

// --- Hooks ---

/** Access the ChatSDK instance */
export function useChatSDK(): ChatSDK;

/** Access conversation state */
export function useConversation(): {
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  sendMessage: (text: string) => Promise<void>;
  sendAction: (actionId: string, payload: unknown) => Promise<void>;
};

/** Access commerce state */
export function useCommerce(): {
  cart: CartState | null;
  activeCheckouts: CheckoutSession[];
  addToCart: (merchantId: string, item: LineItem) => void;
  removeFromCart: (merchantId: string, itemId: string) => void;
  initiateCheckout: (merchantId: string) => Promise<CheckoutSession>;
};

/** Subscribe to SDK events with automatic cleanup */
export function useChatEvent<K extends keyof ChatEventMap>(
  type: K,
  handler: (event: ChatEvent<ChatEventMap[K]>) => void,
  deps?: React.DependencyList
): void;

/** Access widget registration */
export function useWidgetRegistry(): {
  register: <TData, TAction>(def: WidgetDefinition<TData, TAction>) => void;
  unregister: (type: string) => void;
  registeredTypes: string[];
};

// --- Components ---

/** Pre-built chat widget with full UI */
export interface ChatWidgetProps {
  /** Override display mode */
  displayMode?: 'floating' | 'side-panel' | 'inline';
  /** Custom trigger element */
  trigger?: React.ReactNode;
  /** Additional CSS class names */
  className?: string;
  /** Inline style overrides */
  style?: React.CSSProperties;
}

// <ChatWidget displayMode="inline" />

/** Custom trigger button for opening/closing the widget */
export interface ChatTriggerProps {
  children: React.ReactNode | ((state: { isOpen: boolean; unreadCount: number }) => React.ReactNode);
}

// <ChatTrigger>{({ isOpen, unreadCount }) => <MyButton badge={unreadCount} />}</ChatTrigger>
```

---

## 9. Accessibility Specification

```typescript
// ============================================================
// a11y/ — Accessibility module interfaces
// ============================================================

// --- Keyboard Navigation ---

export interface KeyboardManager {
  /** Register a keyboard shortcut */
  registerShortcut(key: string, modifiers: Modifier[], handler: () => void, description: string): void;
  /** Get all registered shortcuts (for help dialog) */
  getShortcuts(): ShortcutDescriptor[];
  /** Enable/disable keyboard management */
  setEnabled(enabled: boolean): void;
}

export type Modifier = 'ctrl' | 'shift' | 'alt' | 'meta';

export interface ShortcutDescriptor {
  key: string;
  modifiers: Modifier[];
  description: string;
}

// Default keyboard navigation contract:
// Tab:              Move between major regions (header, log, input, actions)
// Shift+Tab:        Reverse navigation
// Escape:           Close/minimize widget, return focus to trigger
// Arrow Up/Down:    Navigate between messages (when log is focused)
// Home/End:         Jump to first/last message
// Enter/Space:      Activate focused interactive element
// Ctrl+F6:          Cycle between widget regions (matches Teams convention)

// --- Focus Management ---

export interface FocusManager {
  /** Move focus into the widget (called on open) */
  trapFocus(): void;
  /** Release focus trap and return focus to trigger (called on close) */
  releaseFocus(): void;
  /** Move focus to a specific element within the widget */
  focusElement(element: HTMLElement): void;
  /** Get the element that had focus before the widget opened */
  getPreviousFocus(): HTMLElement | null;
  /** Focus the message input */
  focusInput(): void;
  /** Focus the most recent message */
  focusLastMessage(): void;
}

// --- Screen Reader Announcer ---

export interface Announcer {
  /** Announce text politely (does not interrupt current speech) */
  announcePolite(text: string): void;
  /** Announce text assertively (interrupts current speech) */
  announceAssertive(text: string): void;
  /** Announce a status update (typing indicator, queue position) */
  announceStatus(text: string): void;
  /** Clear the announcement region */
  clear(): void;
}
```

---

## 10. Built-in Widget Schemas

```typescript
// ============================================================
// widgets/schemas.ts — JSON schemas for built-in widgets
// ============================================================

// --- Product Carousel ---

export interface ProductCarouselData {
  title?: string;
  products: ProductCard[];
  /** Action when user selects a product */
  selectionAction: 'view_details' | 'add_to_cart' | 'custom';
}

export interface ProductCard {
  id: string;
  name: string;
  description?: string;
  imageUrl: string;
  imageAlt: string;
  price: Money;
  originalPrice?: Money;     // for showing discounts
  rating?: { score: number; count: number };
  badge?: string;            // "Best Seller", "Sale", etc.
  inStock: boolean;
  merchantId?: string;
  merchantName?: string;
  attributes?: Record<string, string>;
}

// --- Product Comparison ---

export interface ProductComparisonData {
  products: ComparisonProduct[];
  attributes: ComparisonAttribute[];
  highlightBest: boolean;
}

export interface ComparisonProduct {
  id: string;
  name: string;
  imageUrl: string;
  imageAlt: string;
  price: Money;
  merchantId?: string;
  merchantName?: string;
}

export interface ComparisonAttribute {
  name: string;
  values: (string | number | boolean | null)[];
  /** Which product index has the best value for this attribute */
  bestIndex?: number;
  unit?: string;
}

// --- Checkout Flow ---

export interface CheckoutFlowData {
  session: CheckoutSession;
  availableFulfillment: FulfillmentOption[];
  availablePaymentMethods: PaymentMethod[];
  /** Which step to show initially */
  initialStep: 'review' | 'fulfillment' | 'payment' | 'confirm';
}

// --- Order Summary ---

export interface OrderSummaryData {
  items: LineItem[];
  totals: CheckoutTotals;
  fulfillment?: FulfillmentOption;
  paymentMethod?: PaymentMethod;
  discounts?: Discount[];
}

// --- Quick Actions ---

export interface QuickActionsData {
  /** Prompt text shown above the actions */
  prompt?: string;
  actions: ActionButton[];
  /** Layout style */
  layout: 'horizontal' | 'vertical' | 'grid';
  /** Whether actions are single-select or multi-select */
  multiSelect: boolean;
}

// --- Form ---

export interface FormWidgetData {
  title?: string;
  description?: string;
  fields: FormField[];
  submitLabel: string;
  cancelLabel?: string;
}

export type FormField =
  | { type: 'text'; name: string; label: string; required?: boolean; placeholder?: string; validation?: string }
  | { type: 'email'; name: string; label: string; required?: boolean }
  | { type: 'phone'; name: string; label: string; required?: boolean }
  | { type: 'number'; name: string; label: string; required?: boolean; min?: number; max?: number }
  | { type: 'select'; name: string; label: string; required?: boolean; options: { value: string; label: string }[] }
  | { type: 'textarea'; name: string; label: string; required?: boolean; maxLength?: number }
  | { type: 'date'; name: string; label: string; required?: boolean; minDate?: string; maxDate?: string }
  | { type: 'address'; name: string; label: string; required?: boolean };

// --- AP2 Mandate Card ---

export interface MandateCardData {
  mandate: Mandate;
  /** Merchant name and branding */
  merchant: { name: string; logoUrl?: string };
  /** Timeout display (countdown to mandate expiration) */
  showExpiry: boolean;
}

// --- Fulfillment Picker ---

export interface FulfillmentPickerData {
  options: FulfillmentOption[];
  selectedId?: string;
  /** Whether to show delivery window selection inline */
  showWindows: boolean;
}

// --- Rating/Review ---

export interface RatingReviewData {
  prompt: string;
  maxStars: number;
  showTextFeedback: boolean;
  textFeedbackLabel?: string;
}

// --- Order Tracking ---

export interface OrderTrackingData {
  orderId: string;
  merchantOrderId: string;
  status: 'confirmed' | 'processing' | 'shipped' | 'out_for_delivery' | 'delivered' | 'returned';
  statusHistory: { status: string; timestamp: string; description?: string }[];
  trackingUrl?: string;
  estimatedDelivery?: string;
  items: { name: string; imageUrl: string; quantity: number }[];
}
```

---

## 11. Theme Token Specification

```typescript
// ============================================================
// renderer/theme.ts — Design token system
// ============================================================

export interface ThemeTokens {
  // --- Colors (Material Design 3 aligned) ---
  colors: {
    primary: string;
    onPrimary: string;
    primaryContainer: string;
    onPrimaryContainer: string;
    secondary: string;
    onSecondary: string;
    surface: string;
    onSurface: string;
    surfaceContainer: string;
    surfaceContainerHigh: string;
    onSurfaceVariant: string;
    outline: string;
    outlineVariant: string;
    error: string;
    errorContainer: string;
    onErrorContainer: string;
    // Commerce-specific
    success: string;
    onSuccess: string;
    priceHighlight: string;
    discount: string;
  };

  // --- Typography ---
  typography: {
    fontFamily: string;
    titleLarge: TypographyScale;
    titleMedium: TypographyScale;
    titleSmall: TypographyScale;
    bodyLarge: TypographyScale;
    bodyMedium: TypographyScale;
    bodySmall: TypographyScale;
    labelLarge: TypographyScale;
    labelMedium: TypographyScale;
    labelSmall: TypographyScale;
  };

  // --- Shape ---
  shape: {
    cornerSmall: string;       // 8px
    cornerMedium: string;      // 16px
    cornerLarge: string;       // 20px
    cornerExtraLarge: string;  // 28px
    cornerFull: string;        // 100px
  };

  // --- Spacing ---
  spacing: {
    xs: string;    // 4px
    sm: string;    // 8px
    md: string;    // 16px
    lg: string;    // 24px
    xl: string;    // 32px
  };

  // --- Elevation ---
  elevation: {
    level1: string;   // box-shadow
    level2: string;
    level3: string;
  };

  // --- Motion ---
  motion: {
    durationShort: string;     // 150ms
    durationMedium: string;    // 300ms
    durationLong: string;      // 500ms
    easing: string;            // cubic-bezier(...)
  };
}

export interface TypographyScale {
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
  letterSpacing?: string;
}
```

---

## 12. Audit Trail Schema

```typescript
// ============================================================
// Audit trail event schema — for EU AI Act compliance
// Stored in Firestore with BigQuery streaming export
// ============================================================

export interface AuditRecord {
  /** UUIDv7 for time-ordered uniqueness */
  id: string;
  /** ISO 8601 timestamp */
  timestamp: string;
  /** The event that generated this record */
  eventType: string;
  eventId: string;
  /** Session and conversation identifiers */
  sessionId: string;
  conversationId: string;
  /** User identity (hashed/pseudonymized for privacy) */
  userIdHash: string;
  /** Agent identity */
  agentId: string;
  agentRole: string;
  /** What happened */
  action: AuditAction;
  /** Outcome */
  outcome: 'success' | 'failure' | 'pending' | 'cancelled';
  /** Commerce-specific fields */
  commerce?: {
    merchantId?: string;
    checkoutSessionId?: string;
    mandateId?: string;
    mandateType?: MandateType;
    amount?: Money;
    orderId?: string;
  };
  /** Agent reasoning trace (for explainability) */
  reasoning?: string;
  /** Hash of the full event payload (for tamper detection) */
  payloadHash: string;
}

export type AuditAction =
  | 'message_sent'
  | 'message_received'
  | 'widget_rendered'
  | 'widget_interaction'
  | 'cart_modified'
  | 'checkout_initiated'
  | 'checkout_state_changed'
  | 'mandate_presented'
  | 'mandate_signed'
  | 'mandate_rejected'
  | 'payment_initiated'
  | 'payment_completed'
  | 'payment_failed'
  | 'agent_handoff'
  | 'human_escalation'
  | 'session_started'
  | 'session_ended'
  | 'error_occurred';

// The audit logger is a single subscriber on the event bus:
//
//   eventBus.onAny((event) => {
//     const record = createAuditRecord(event);
//     auditStore.write(record);
//     auditStream.push(record);  // real-time BigQuery export
//   });
//
// This is why building audit into the event bus from day one matters.
// Retrofitting it later means instrumenting every component individually.
```

---

## 13. Embedded Checkout Bridge (JSON-RPC 2.0)

```typescript
// ============================================================
// commerce/embedded-checkout.ts
// Implements UCP's Embedded Checkout Protocol for requires_escalation
// ============================================================

// The bridge uses JSON-RPC 2.0 over postMessage between the SDK
// (parent window) and the merchant's checkout page (iframe).

export interface EmbeddedCheckoutBridge {
  /** Open the merchant's embedded checkout in a sandboxed iframe */
  open(config: EmbeddedCheckoutConfig): Promise<EmbeddedCheckoutResult>;
  /** Close the embedded checkout (user cancelled or completed) */
  close(): void;
  /** Check if an embedded checkout is currently active */
  readonly isActive: boolean;
}

export interface EmbeddedCheckoutConfig {
  /** URL from UCP's requires_escalation response */
  continueUrl: string;
  /** UCP checkout session ID */
  sessionId: string;
  /** Iframe sandbox attributes (strict by default) */
  sandbox?: string;
  /** Maximum time to wait for merchant page to load */
  timeoutMs?: number;
  /** Callback for progress updates from merchant */
  onProgress?: (step: string) => void;
}

// JSON-RPC 2.0 messages exchanged between SDK and merchant iframe:

/** SDK → Merchant: Initialize checkout context */
interface InitMessage {
  jsonrpc: '2.0';
  method: 'checkout.init';
  params: {
    sessionId: string;
    locale: string;
    theme: Partial<ThemeTokens>;
  };
  id: string;
}

/** Merchant → SDK: Report checkout progress */
interface ProgressMessage {
  jsonrpc: '2.0';
  method: 'checkout.progress';
  params: {
    step: string;          // 'shipping_selected', 'payment_entered', etc.
    data?: unknown;
  };
}

/** Merchant → SDK: Checkout completed */
interface CompleteMessage {
  jsonrpc: '2.0';
  method: 'checkout.complete';
  params: {
    orderId: string;
    status: 'success';
  };
}

/** Merchant → SDK: Request to resize iframe */
interface ResizeMessage {
  jsonrpc: '2.0';
  method: 'checkout.resize';
  params: {
    height: number;
  };
}

/** SDK → Merchant: Close/cancel */
interface CancelMessage {
  jsonrpc: '2.0';
  method: 'checkout.cancel';
  params: {
    reason: 'user_cancelled' | 'timeout' | 'error';
  };
  id: string;
}
```

---

## 14. Performance Budgets

| Module | Max Size (gzipped) | Load Strategy | Trigger |
|--------|-------------------|---------------|---------|
| Core runtime | 30 KB | Immediate | Script tag |
| Widget registry + built-in text/card | 15 KB | Immediate | Script tag |
| Accessibility layer | 8 KB | Immediate | Script tag |
| Theme engine | 5 KB | Immediate | Script tag |
| **Total initial bundle** | **58 KB** | **Immediate** | **Script tag** |
| Commerce engine | 25 KB | Lazy | First `commerce:*` event |
| Streaming renderer | 6 KB | Lazy | First `message:stream-start` event |
| Analytics collector | 4 KB | Lazy | First `trackEvent()` call or after 5s idle |
| Voice input | 12 KB | Lazy | User activates microphone |
| Individual widget renderers | 3-8 KB each | Lazy | First render of that widget type |
| React SDK | 5 KB | N/A | Separate npm package |
| Web Components SDK | 4 KB | N/A | Separate npm package |

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial bundle parse time (mobile 4G) | <100ms | Chrome DevTools |
| Time-to-interactive after script load | <200ms | Lighthouse |
| First widget render (cached module) | <100ms | Custom performance mark |
| First widget render (lazy load) | <300ms | Custom performance mark |
| Streaming text time-to-first-character | <50ms from stream start | Custom performance mark |
| Core Web Vitals impact (CLS) | <0.01 | Lighthouse |
| Core Web Vitals impact (INP) | <50ms | Lighthouse |
| Memory footprint (idle, no conversation) | <5 MB | Chrome DevTools |
| Memory footprint (active, 100 messages) | <15 MB | Chrome DevTools |

---

*This specification is intended to be directly translatable into TypeScript source code. All interfaces use TypeScript syntax and conventions. JSON Schema references use the JSON Schema Draft 7 specification.*

*Document version: 1.0*
*Last updated: February 2026*
