// src/components/PropertyGrid.tsx
// ─────────────────────────────────────────────────────────────────────────────
// Pure presentation component — no data, no filter logic.
//
// WHAT CHANGED FROM ORIGINAL:
//   - Mock data array removed → lives in src/data/properties.ts
//   - Filter logic removed    → lives in src/hooks/usePropertyFilters.ts
//   - FilterTab type removed  → lives in src/hooks/usePropertyFilters.ts
//   - This file now only handles: rendering tabs, grid, and load-more button
//
// WIRING UP THE REAL API (when ready):
//   Replace the MOCK_PROPERTIES import with a useProperties() hook call.
//   The component and filter hook don't need to change at all.
//   Example:
//     const { data, isLoading } = useProperties({ status: "ACTIVE" });
//     const properties = data?.results ?? [];
// ─────────────────────────────────────────────────────────────────────────────

import React from "react";
import { motion } from "framer-motion";
import { ChevronRightIcon } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { MOCK_PROPERTIES } from "../data/properties";
import { usePropertyFilters, FILTER_TABS } from "../hooks/usePropertyFilters";

// Animation variants — defined outside component to avoid re-creation on render
const gridVariants = {
  visible: {
    transition: { staggerChildren: 0.08 },
  },
};

const cardVariants = {
  hidden:  { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export function PropertyGrid() {
  // Data source: swap MOCK_PROPERTIES for API data when ready
  const properties = MOCK_PROPERTIES;

  // Filter logic lives in the hook — component stays clean
  const { activeTab, setActiveTab, filteredProperties } =
    usePropertyFilters(properties);

  return (
    <section className="py-16 bg-white dark:bg-[#0A1A10]" id="listings">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <h2 className="font-heading text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Featured Verified Listings
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-body text-sm">
              All properties independently verified by licensed surveyors
            </p>
          </div>
          <a
            href="#"
            className="flex items-center gap-1 text-sm font-semibold text-forest dark:text-gold hover:text-forest-light transition-colors"
          >
            View all listings
            <ChevronRightIcon className="w-4 h-4" />
          </a>
        </div>

        {/* Filter Tabs */}
        <FilterTabs
          tabs={FILTER_TABS}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {/* Property Grid */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={gridVariants}
        >
          {filteredProperties.map((property) => (
            <motion.div key={property.id} variants={cardVariants}>
              <PropertyCard
                title={property.title}
                location={property.location}
                price={property.price}
                size={property.size}
                type={property.type}
                isVerifiedPro={property.isVerifiedPro}
                lastVerified={property.lastVerified}
                imageUrl={property.imageUrl}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* Empty state */}
        {filteredProperties.length === 0 && (
          <EmptyState activeTab={activeTab} />
        )}

        {/* Load More */}
        <div className="flex justify-center mt-10">
          <button className="flex items-center gap-2 px-8 py-3 text-sm font-semibold text-forest dark:text-gold border-2 border-forest dark:border-gold rounded-xl hover:bg-forest hover:text-white dark:hover:bg-gold dark:hover:text-forest transition-colors">
            Load More Listings
            <ChevronRightIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────
// Small focused components extracted to keep PropertyGrid readable.

interface FilterTabsProps {
  tabs: readonly string[];
  activeTab: string;
  onTabChange: (tab: any) => void;
}

function FilterTabs({ tabs, activeTab, onTabChange }: FilterTabsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 mb-8 scrollbar-hide">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onTabChange(tab)}
          className={`flex-shrink-0 px-4 py-2 text-sm font-medium rounded-full border transition-all ${
            activeTab === tab
              ? "bg-forest text-white border-forest"
              : "bg-white dark:bg-[#122B1A] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-[#1F3D28] hover:border-forest hover:text-forest dark:hover:border-gold dark:hover:text-gold"
          }`}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}

interface EmptyStateProps {
  activeTab: string;
}

function EmptyState({ activeTab }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <p className="text-gray-400 dark:text-gray-500 font-body text-sm">
        No listings found for{" "}
        <span className="font-semibold text-forest dark:text-gold">
          {activeTab}
        </span>
        .
      </p>
      <p className="text-gray-300 dark:text-gray-600 font-body text-xs mt-1">
        Try a different filter or check back later.
      </p>
    </div>
  );
}
