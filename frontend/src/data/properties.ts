// src/data/properties.ts
// ─────────────────────────────────────────────────────────────────────────────
// Static mock data for development.
// When API communication is wired up, replace this with a call to
// propertyApi.list() from src/api/endpoints.ts.
// The PropertyListing type mirrors PropertyListSerializer in the backend.
// ─────────────────────────────────────────────────────────────────────────────

export type LandType =
  | "Residential"
  | "Agricultural"
  | "Commercial"
  | "Industrial";

export interface PropertyListing {
  id: number;
  title: string;
  location: string;
  price: string;
  priceRaw: number;        // raw KES value for filtering
  size: string;
  sizeRaw: number;         // raw acres value for filtering
  type: LandType;
  isVerifiedPro: boolean;
  lastVerified: string;
  imageUrl?: string;
}

export const MOCK_PROPERTIES: PropertyListing[] = [
  {
    id: 1,
    title: "Prime Residential Plot – Karen",
    location: "Karen, Nairobi",
    price: "KES 8,500,000",
    priceRaw: 8_500_000,
    size: "0.5 Acres",
    sizeRaw: 0.5,
    type: "Residential",
    isVerifiedPro: true,
    lastVerified: "2 days ago",
  },
  {
    id: 2,
    title: "Agricultural Land – Nakuru",
    location: "Nakuru County",
    price: "KES 2,200,000",
    priceRaw: 2_200_000,
    size: "5 Acres",
    sizeRaw: 5,
    type: "Agricultural",
    isVerifiedPro: false,
    lastVerified: "5 days ago",
  },
  {
    id: 3,
    title: "Commercial Plot – Westlands",
    location: "Westlands, Nairobi",
    price: "KES 45,000,000",
    priceRaw: 45_000_000,
    size: "0.25 Acres",
    sizeRaw: 0.25,
    type: "Commercial",
    isVerifiedPro: true,
    lastVerified: "1 day ago",
  },
  {
    id: 4,
    title: "Beach Plot – Diani",
    location: "Kwale County",
    price: "KES 12,000,000",
    priceRaw: 12_000_000,
    size: "0.75 Acres",
    sizeRaw: 0.75,
    type: "Residential",
    isVerifiedPro: false,
    lastVerified: "7 days ago",
  },
  {
    id: 5,
    title: "Farm Land – Eldoret",
    location: "Uasin Gishu County",
    price: "KES 3,800,000",
    priceRaw: 3_800_000,
    size: "10 Acres",
    sizeRaw: 10,
    type: "Agricultural",
    isVerifiedPro: true,
    lastVerified: "3 days ago",
  },
  {
    id: 6,
    title: "Industrial Plot – Athi River",
    location: "Machakos County",
    price: "KES 18,500,000",
    priceRaw: 18_500_000,
    size: "2 Acres",
    sizeRaw: 2,
    type: "Commercial",
    isVerifiedPro: false,
    lastVerified: "4 days ago",
  },
];
