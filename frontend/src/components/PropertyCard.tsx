import React from 'react';
import { motion } from 'framer-motion';
import {
  ShieldCheckIcon,
  CrownIcon,
  MapPinIcon,
  ClockIcon,
  HomeIcon,
  MessageCircleIcon } from
'lucide-react';
type LandType = 'Residential' | 'Agricultural' | 'Commercial' | 'Industrial';
interface PropertyCardProps {
  title: string;
  location: string;
  price: string;
  size: string;
  type: LandType;
  isVerifiedPro: boolean;
  lastVerified: string;
  imageUrl?: string;
}
const TYPE_COLORS: Record<LandType, string> = {
  Residential:
  'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800',
  Agricultural:
  'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
  Commercial:
  'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-300 dark:border-orange-800',
  Industrial:
  'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800/50 dark:text-gray-300 dark:border-gray-700'
};
const GRADIENT_COLORS: Record<LandType, string> = {
  Residential: 'from-forest/80 to-forest-light/60',
  Agricultural: 'from-green-800/80 to-green-600/60',
  Commercial: 'from-amber-800/80 to-amber-600/60',
  Industrial: 'from-gray-700/80 to-gray-500/60'
};
export function PropertyCard({
  title,
  location,
  price,
  size,
  type,
  isVerifiedPro,
  lastVerified,
  imageUrl
}: PropertyCardProps) {
  return (
    <motion.article
      className="bg-white dark:bg-[#122B1A] rounded-2xl overflow-hidden shadow-card hover:shadow-card-hover transition-all duration-300 border border-gray-100 dark:border-[#1F3D28] flex flex-col"
      whileHover={{
        y: -4
      }}
      transition={{
        duration: 0.2
      }}>

      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        {imageUrl ?
        <img
          src={imageUrl}
          alt={title}
          className="w-full h-full object-cover" /> :


        <div
          className={`w-full h-full bg-gradient-to-br ${GRADIENT_COLORS[type]} flex items-center justify-center`}>

            <HomeIcon className="w-12 h-12 text-white/40" />
          </div>
        }

        {/* Verified Badge */}
        <div className="absolute top-3 left-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-forest rounded-full shadow-md">
            <ShieldCheckIcon className="w-3.5 h-3.5 text-gold" />
            <span className="text-xs font-semibold text-white">Verified</span>
          </div>
        </div>

        {/* Verified Pro Badge */}
        {isVerifiedPro &&
        <div className="absolute top-3 right-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-[#0A1A10] rounded-full shadow-md border border-gold/30">
              <CrownIcon className="w-3.5 h-3.5 text-gold" />
              <span className="text-xs font-semibold text-gold-dark">
                Verified Pro
              </span>
            </div>
          </div>
        }

        {/* Land Type Chip */}
        <div className="absolute bottom-3 left-3">
          <span
            className={`px-2.5 py-1 text-xs font-medium rounded-full border ${TYPE_COLORS[type]} bg-white/90 dark:bg-black/50 backdrop-blur-sm`}>

            {type}
          </span>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-5 flex flex-col flex-1">
        <h3 className="font-heading text-base font-semibold text-gray-900 dark:text-white mb-2 leading-snug line-clamp-2">
          {title}
        </h3>

        <div className="flex items-center gap-1.5 mb-3">
          <MapPinIcon className="w-3.5 h-3.5 text-forest dark:text-gold flex-shrink-0" />
          <span className="text-sm text-gray-500 dark:text-gray-400 font-body">
            {location}
          </span>
        </div>

        <div className="flex items-end justify-between mb-3">
          <div>
            <div className="font-heading text-xl font-bold text-forest dark:text-gold">
              {price}
            </div>
            <div className="text-xs text-gray-400 dark:text-gray-500 font-body mt-0.5">
              {size}
            </div>
          </div>
        </div>

        {/* Last Verified */}
        <div className="flex items-center gap-1.5 py-2.5 px-3 bg-green-50 dark:bg-forest/20 rounded-lg border border-green-100 dark:border-forest/30 mb-4">
          <ClockIcon className="w-3.5 h-3.5 text-forest dark:text-gold flex-shrink-0" />
          <span className="text-xs text-forest dark:text-gold font-medium font-body">
            Last verified: {lastVerified}
          </span>
        </div>

        {/* CTA Buttons */}
        <div className="flex items-center gap-2 mt-auto">
          <button className="flex-1 py-2 text-sm font-semibold text-forest dark:text-gold border border-forest dark:border-gold rounded-lg hover:bg-forest hover:text-white dark:hover:bg-gold dark:hover:text-forest transition-colors">
            View Details
          </button>
          <button className="flex items-center gap-1 px-3 py-2 text-sm font-semibold text-white bg-forest dark:bg-gold dark:text-forest rounded-lg hover:bg-forest-light dark:hover:bg-gold-light transition-colors">
            <MessageCircleIcon className="w-3.5 h-3.5" />
            Message
          </button>
        </div>
      </div>
    </motion.article>);

}