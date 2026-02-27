import React, { useState, Children } from 'react';
import { motion } from 'framer-motion';
import { ChevronRightIcon } from 'lucide-react';
import { PropertyCard } from './PropertyCard';
type FilterTab =
'All' |
'Residential' |
'Agricultural' |
'Commercial' |
'Under 1 Acre';
const FILTER_TABS: FilterTab[] = [
'All',
'Residential',
'Agricultural',
'Commercial',
'Under 1 Acre'];

const PROPERTIES = [
{
  id: 1,
  title: 'Prime Residential Plot – Karen',
  location: 'Karen, Nairobi',
  price: 'KES 8,500,000',
  size: '0.5 Acres',
  type: 'Residential' as const,
  isVerifiedPro: true,
  lastVerified: '2 days ago'
},
{
  id: 2,
  title: 'Agricultural Land – Nakuru',
  location: 'Nakuru County',
  price: 'KES 2,200,000',
  size: '5 Acres',
  type: 'Agricultural' as const,
  isVerifiedPro: false,
  lastVerified: '5 days ago'
},
{
  id: 3,
  title: 'Commercial Plot – Westlands',
  location: 'Westlands, Nairobi',
  price: 'KES 45,000,000',
  size: '0.25 Acres',
  type: 'Commercial' as const,
  isVerifiedPro: true,
  lastVerified: '1 day ago'
},
{
  id: 4,
  title: 'Beach Plot – Diani',
  location: 'Kwale County',
  price: 'KES 12,000,000',
  size: '0.75 Acres',
  type: 'Residential' as const,
  isVerifiedPro: false,
  lastVerified: '7 days ago'
},
{
  id: 5,
  title: 'Farm Land – Eldoret',
  location: 'Uasin Gishu County',
  price: 'KES 3,800,000',
  size: '10 Acres',
  type: 'Agricultural' as const,
  isVerifiedPro: true,
  lastVerified: '3 days ago'
},
{
  id: 6,
  title: 'Industrial Plot – Athi River',
  location: 'Machakos County',
  price: 'KES 18,500,000',
  size: '2 Acres',
  type: 'Commercial' as const,
  isVerifiedPro: false,
  lastVerified: '4 days ago'
}];

export function PropertyGrid() {
  const [activeTab, setActiveTab] = useState<FilterTab>('All');
  const filteredProperties = PROPERTIES.filter((p) => {
    if (activeTab === 'All') return true;
    if (activeTab === 'Under 1 Acre') return parseFloat(p.size) < 1;
    return p.type === activeTab;
  });
  return (
    <section className="py-16 bg-white dark:bg-[#0A1A10]" id="listings">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
            className="flex items-center gap-1 text-sm font-semibold text-forest dark:text-gold hover:text-forest-light transition-colors">

            View all listings
            <ChevronRightIcon className="w-4 h-4" />
          </a>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-8 scrollbar-hide">
          {FILTER_TABS.map((tab) =>
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-shrink-0 px-4 py-2 text-sm font-medium rounded-full border transition-all ${activeTab === tab ? 'bg-forest text-white border-forest' : 'bg-white dark:bg-[#122B1A] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-[#1F3D28] hover:border-forest hover:text-forest dark:hover:border-gold dark:hover:text-gold'}`}>

              {tab}
            </button>
          )}
        </div>

        {/* Grid */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
          initial="hidden"
          whileInView="visible"
          viewport={{
            once: true
          }}
          variants={{
            visible: {
              transition: {
                staggerChildren: 0.08
              }
            }
          }}>

          {filteredProperties.map((property) =>
          <motion.div
            key={property.id}
            variants={{
              hidden: {
                opacity: 0,
                y: 20
              },
              visible: {
                opacity: 1,
                y: 0,
                transition: {
                  duration: 0.5
                }
              }
            }}>

              <PropertyCard {...property} />
            </motion.div>
          )}
        </motion.div>

        <div className="flex justify-center mt-10">
          <button className="flex items-center gap-2 px-8 py-3 text-sm font-semibold text-forest dark:text-gold border-2 border-forest dark:border-gold rounded-xl hover:bg-forest hover:text-white dark:hover:bg-gold dark:hover:text-forest transition-colors">
            Load More Listings
            <ChevronRightIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>);

}