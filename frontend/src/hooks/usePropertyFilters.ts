// src/hooks/usePropertyFilters.ts
// ─────────────────────────────────────────────────────────────────────────────
// Encapsulates all filter state and filter logic for the property grid.
// Extracted from PropertyGrid.tsx so it can be:
//   - tested in isolation
//   - reused by other components (e.g. a map view)
//   - extended without touching rendering code
//
// FILTER TABS:
//   "All"          → no filter
//   "Residential"  → type === "Residential"
//   "Agricultural" → type === "Agricultural"
//   "Commercial"   → type === "Commercial"
//   "Under 1 Acre" → sizeRaw < 1
//
// EXTENDING:
//   To add a price range filter, add a priceRange state here and a
//   filter condition in the filteredProperties useMemo below.
//   The component never needs to change.
// ─────────────────────────────────────────────────────────────────────────────

import { useState, useMemo } from "react";
import { PropertyListing, LandType } from "../data/properties";

export type FilterTab =
  | "All"
  | "Residential"
  | "Agricultural"
  | "Commercial"
  | "Under 1 Acre";

export const FILTER_TABS: FilterTab[] = [
  "All",
  "Residential",
  "Agricultural",
  "Commercial",
  "Under 1 Acre",
];

interface UsePropertyFiltersReturn {
  activeTab: FilterTab;
  setActiveTab: (tab: FilterTab) => void;
  filteredProperties: PropertyListing[];
}

export function usePropertyFilters(
  properties: PropertyListing[]
): UsePropertyFiltersReturn {
  const [activeTab, setActiveTab] = useState<FilterTab>("All");

  const filteredProperties = useMemo(() => {
    switch (activeTab) {
      case "All":
        return properties;

      case "Under 1 Acre":
        return properties.filter((p) => p.sizeRaw < 1);

      // Type-based filters: Residential, Agricultural, Commercial
      default:
        return properties.filter((p) => p.type === (activeTab as LandType));
    }
  }, [properties, activeTab]);

  return {
    activeTab,
    setActiveTab,
    filteredProperties,
  };
}
