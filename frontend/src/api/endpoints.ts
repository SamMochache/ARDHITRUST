// src/api/endpoints.ts
// ─────────────────────────────────────────────────────────────────────────────
// One function per backend endpoint.  Types mirror your Django serializers.
// ─────────────────────────────────────────────────────────────────────────────

import { api } from "./client";

// ════════════════════════════════════════════════════════════════════════════
// TYPES  (keep in sync with serializers.py)
// ════════════════════════════════════════════════════════════════════════════

export interface User {
  id: string;
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
  role: "BUYER" | "SELLER" | "ADMIN" | "SURVEYOR" | "VALUER";
  email_verified: boolean;
  phone_verified: boolean;
  kyc_status: "PENDING" | "IN_REVIEW" | "APPROVED" | "REJECTED" | null;
  created_at: string;
}

export interface KYCStatus {
  status: "PENDING" | "IN_REVIEW" | "APPROVED" | "REJECTED";
  iprs_verified: boolean;
  kra_verified: boolean;
  rejection_reason: string;
  submitted_at: string | null;
  reviewed_at: string | null;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface Property {
  id: string;
  title: string;
  area_name: string;
  county: string;
  price: string;         // "KES 8,500,000"  (formatted by serializer)
  size: string;          // "0.5 Acres"
  property_type: "RESIDENTIAL" | "AGRICULTURAL" | "COMMERCIAL" | "INDUSTRIAL";
  is_verified_pro: boolean;
  trust_score: number;
  last_verified: string;
  status: string;
}

export interface PropertyDetail extends Property {
  description: string;
  sub_county: string;
  latitude: number | null;
  longitude: number | null;
  lr_number: string;
  price_negotiable: boolean;
  seller_name: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  next: string | null;
  previous: string | null;
}

export interface EscrowTransaction {
  escrow_id: string;
  status: string;
  amount_kes: number;
  platform_fee_kes: number;
  mpesa_checkout_request_id: string;
}

export interface ValuationResult {
  property_id: string;
  cached: boolean;
  estimated_value_kes: number;
  estimated_min_kes: number;
  estimated_max_kes: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  comparables_used: number;
  price_per_acre: number;
  narrative_en: string;
  narrative_sw: string;
  comparable_sales: Array<{
    price_kes: number;
    size_acres: number;
    county: string;
    property_type: string;
  }>;
  methodology: string;
}

export interface AssistantReply {
  reply: string;
  session_key: string;
}

export interface VerificationStatus {
  status: string;
  trust_score: number;
  verified_at: string | null;
  result: {
    ownership_confirmed?: boolean;
    registered_owner?: string;
    caveat_present?: boolean;
    rates_cleared?: boolean;
    encumbrances_count?: number;
  };
}

// ════════════════════════════════════════════════════════════════════════════
// AUTH
// ════════════════════════════════════════════════════════════════════════════

export const authApi = {
  /**
   * POST /api/v1/auth/register/
   * Anyone can register (AllowAny). Returns UserSerializer data.
   */
  register: (data: {
    email: string;
    phone: string;
    first_name: string;
    last_name: string;
    role: "BUYER" | "SELLER";
    password: string;
    password2: string;
  }) => api.post<User>("/api/v1/auth/register/", data),

  /**
   * POST /api/v1/auth/token/
   * Returns {access, refresh}. Store both via tokenStore.set().
   */
  login: (email: string, password: string) =>
    api.post<TokenResponse>("/api/v1/auth/token/", { email, password }),

  /**
   * GET /api/v1/auth/me/
   * Returns the current user. Protected — requires valid access token.
   */
  me: () => api.get<User>("/api/v1/auth/me/"),

  /**
   * POST /api/v1/auth/kyc/submit/
   * Rate-limited: 3/hour. Triggers async KYC Celery task.
   */
  submitKYC: (data: {
    national_id: string;
    kra_pin: string;
    id_front_key: string;
    id_back_key: string;
  }) => api.post<{ detail: string }>("/api/v1/auth/kyc/submit/", data),

  /**
   * GET /api/v1/auth/kyc/status/
   */
  kycStatus: () => api.get<KYCStatus>("/api/v1/auth/kyc/status/"),
};

// ════════════════════════════════════════════════════════════════════════════
// PROPERTIES
// ════════════════════════════════════════════════════════════════════════════

export const propertyApi = {
  /**
   * GET /api/v1/properties/?county=Nairobi&property_type=RESIDENTIAL&...
   * Public endpoint. Supports all PropertyFilter fields + ordering.
   */
  list: (params?: Record<string, string | number>) => {
    const qs = params
      ? "?" + new URLSearchParams(
          Object.fromEntries(
            Object.entries(params).map(([k, v]) => [k, String(v)])
          )
        ).toString()
      : "";
    return api.get<PaginatedResponse<Property>>(`/api/v1/properties/${qs}`);
  },

  /**
   * GET /api/v1/properties/<uuid>/
   * Public. Returns PropertyDetailSerializer.
   */
  detail: (id: string) =>
    api.get<PropertyDetail>(`/api/v1/properties/${id}/`),

  /**
   * POST /api/v1/properties/create/
   * Requires IsVerifiedSeller (KYC approved + SELLER role).
   * Triggers initiate_ardhisasa_check Celery task automatically.
   */
  create: (data: {
    title: string;
    description: string;
    county: string;
    area_name: string;
    lr_number: string;
    property_type: string;
    size_acres: string;
    price_kes: number;
    price_negotiable?: boolean;
    latitude?: number;
    longitude?: number;
  }) => api.post<PropertyDetail>("/api/v1/properties/create/", data),

  /**
   * GET /api/v1/properties/mine/
   * Returns all listings for the current seller (all statuses).
   */
  myListings: () =>
    api.get<PaginatedResponse<PropertyDetail>>("/api/v1/properties/mine/"),

  /**
   * PATCH /api/v1/properties/<uuid>/update/
   * Requires IsPropertyOwner.
   */
  update: (id: string, data: Partial<PropertyDetail>) =>
    api.patch<PropertyDetail>(`/api/v1/properties/${id}/update/`, data),
};

// ════════════════════════════════════════════════════════════════════════════
// VERIFICATION
// ════════════════════════════════════════════════════════════════════════════

export const verificationApi = {
  /**
   * GET /api/v1/verification/<property_id>/status/
   * Shows Ardhisasa results + trust score. Protected.
   */
  status: (propertyId: string) =>
    api.get<VerificationStatus>(`/api/v1/verification/${propertyId}/status/`),

  /**
   * POST /api/v1/verification/request/
   * Triggers re-verification. Only the property owner can call this.
   */
  request: (propertyId: string) =>
    api.post<{ detail: string }>("/api/v1/verification/request/", {
      property_id: propertyId,
    }),
};

// ════════════════════════════════════════════════════════════════════════════
// ESCROW
// ════════════════════════════════════════════════════════════════════════════

export const escrowApi = {
  /**
   * POST /api/v1/escrow/initiate/
   * Requires IsKYCApproved. Fires STK push via M-Pesa.
   */
  initiate: (propertyId: string) =>
    api.post<EscrowTransaction>("/api/v1/escrow/initiate/", {
      property_id: propertyId,
    }),

  /**
   * GET /api/v1/escrow/<uuid>/status/
   * Only buyer, seller, or staff can view.
   */
  status: (escrowId: string) =>
    api.get<{
      id: string;
      status: string;
      amount_kes: number;
      platform_fee: number;
      property: string;
      buyer: string;
      seller: string;
      funds_released: string | null;
      created_at: string;
    }>(`/api/v1/escrow/${escrowId}/status/`),
};

// ════════════════════════════════════════════════════════════════════════════
// AI AGENTS
// ════════════════════════════════════════════════════════════════════════════

export const agentApi = {
  /**
   * POST /api/v1/agents/assistant/
   * Rate-limited: 10/minute (AIAgentThrottle).
   * Pass session_key to maintain conversation history (stored in Redis).
   */
  chat: (message: string, sessionKey?: string, propertyId?: string) =>
    api.post<AssistantReply>("/api/v1/agents/assistant/", {
      message,
      session_key: sessionKey,
      property_id: propertyId,
    }),

  /**
   * POST /api/v1/agents/valuation/
   * Returns hedonic model estimate + Claude narrative.
   * Rate-limited: 10/minute. Results cached by input hash.
   */
  valuation: (propertyId: string) =>
    api.post<ValuationResult>("/api/v1/agents/valuation/", {
      property_id: propertyId,
    }),
};

// ════════════════════════════════════════════════════════════════════════════
// MESSAGING
// ════════════════════════════════════════════════════════════════════════════

export const messagingApi = {
  /**
   * GET /api/v1/messaging/conversations/
   * Returns the current user's conversations.
   */
  conversations: () =>
    api.get<PaginatedResponse<{
      id: string;
      property_title: string;
      other_party: { id: string; name: string };
      last_message: { timestamp: string } | null;
      created_at: string;
    }>>("/api/v1/messaging/conversations/"),

  /**
   * POST /api/v1/messaging/conversations/create/
   * Idempotent — returns 201 on first call, 200 if already exists.
   */
  startConversation: (propertyId: string) =>
    api.post<{ id: string }>("/api/v1/messaging/conversations/create/", {
      property_id: propertyId,
    }),

  /**
   * GET /api/v1/messaging/conversations/<uuid>/messages/
   */
  messages: (conversationId: string) =>
    api.get<PaginatedResponse<{
      id: string;
      sender_name: string;
      body_encrypted: string;
      read_at: string | null;
      created_at: string;
    }>>(`/api/v1/messaging/conversations/${conversationId}/messages/`),
};

// ════════════════════════════════════════════════════════════════════════════
// HEALTH
// ════════════════════════════════════════════════════════════════════════════

export const healthApi = {
  /** GET /api/health/ — fast liveness check */
  ping: () => api.get<{ status: string; version: string }>("/api/health/"),
};
