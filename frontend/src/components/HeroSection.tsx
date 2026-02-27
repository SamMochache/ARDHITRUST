import React, { useState, Fragment } from 'react';
import { motion } from 'framer-motion';
import {
  ShieldCheckIcon,
  MapPinIcon,
  SearchIcon,
  CheckCircleIcon,
  UsersIcon } from
'lucide-react';
const QUICK_FILTERS = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'All Counties'];
const LAND_TYPES = [
'All Types',
'Residential',
'Agricultural',
'Commercial',
'Industrial'];

const SIZE_RANGES = [
'Any Size',
'Under 0.5 Acres',
'0.5–2 Acres',
'2–10 Acres',
'10+ Acres'];

const fadeUp = {
  hidden: {
    opacity: 0,
    y: 24
  },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.6,
      ease: 'easeOut'
    }
  })
};
export function HeroSection() {
  const [location, setLocation] = useState('');
  const [landType, setLandType] = useState('All Types');
  const [sizeRange, setSizeRange] = useState('Any Size');
  const [activeFilter, setActiveFilter] = useState('All Counties');
  return (
    <section className="relative bg-cream dark:bg-[#0F2318] overflow-hidden">
      {/* Background pattern */}
      <div
        className="absolute inset-0 opacity-[0.03] dark:opacity-[0.06]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231B4332' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />


      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20">
        {/* Verified Badge */}
        <motion.div
          className="flex justify-center mb-8"
          custom={0}
          initial="hidden"
          animate="visible"
          variants={fadeUp}>

          <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-forest rounded-full border-2 border-gold shadow-lg">
            <ShieldCheckIcon className="w-4 h-4 text-gold" />
            <span className="text-sm font-semibold text-white tracking-wide uppercase">
              Verified Listings Only
            </span>
            <div className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse" />
          </div>
        </motion.div>

        {/* Headline */}
        <motion.div
          className="text-center max-w-4xl mx-auto mb-6"
          custom={1}
          initial="hidden"
          animate="visible"
          variants={fadeUp}>

          <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight mb-4">
            Buy Land You Can{' '}
            <span className="text-forest dark:text-gold relative">
              Trust
              <svg
                className="absolute -bottom-2 left-0 w-full"
                viewBox="0 0 200 8"
                fill="none"
                xmlns="http://www.w3.org/2000/svg">

                <path
                  d="M2 6C50 2 100 2 198 6"
                  stroke="#D4AF37"
                  strokeWidth="3"
                  strokeLinecap="round" />

              </svg>
            </span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 font-body max-w-2xl mx-auto leading-relaxed">
            Every listing verified by licensed surveyors.{' '}
            <span className="text-forest dark:text-gold font-medium">
              Protected by Digital Escrow.
            </span>
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          className="max-w-4xl mx-auto mb-6"
          custom={2}
          initial="hidden"
          animate="visible"
          variants={fadeUp}>

          <div className="bg-white dark:bg-[#122B1A] rounded-2xl shadow-xl border border-gray-100 dark:border-[#1F3D28] p-3">
            <div className="flex flex-col md:flex-row gap-3">
              <div className="flex-1 relative">
                <MapPinIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-forest" />
                <input
                  type="text"
                  placeholder="Location (e.g. Karen, Nairobi)"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 text-sm text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50 dark:bg-[#0F2318] rounded-xl border border-gray-200 dark:border-[#1F3D28] focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-all" />

              </div>
              <div className="md:w-44">
                <select
                  value={landType}
                  onChange={(e) => setLandType(e.target.value)}
                  className="w-full px-4 py-3 text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-[#0F2318] rounded-xl border border-gray-200 dark:border-[#1F3D28] focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-all appearance-none cursor-pointer">

                  {LAND_TYPES.map((type) =>
                  <option key={type} value={type}>
                      {type}
                    </option>
                  )}
                </select>
              </div>
              <div className="md:w-44">
                <select
                  value={sizeRange}
                  onChange={(e) => setSizeRange(e.target.value)}
                  className="w-full px-4 py-3 text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-[#0F2318] rounded-xl border border-gray-200 dark:border-[#1F3D28] focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-all appearance-none cursor-pointer">

                  {SIZE_RANGES.map((size) =>
                  <option key={size} value={size}>
                      {size}
                    </option>
                  )}
                </select>
              </div>
              <button className="flex items-center justify-center gap-2 px-8 py-3 bg-forest text-white text-sm font-semibold rounded-xl hover:bg-forest-light transition-colors shadow-md">
                <SearchIcon className="w-4 h-4" />
                Search Land
              </button>
            </div>
          </div>
        </motion.div>

        {/* Quick Filter Chips */}
        <motion.div
          className="flex flex-wrap justify-center gap-2 mb-12"
          custom={3}
          initial="hidden"
          animate="visible"
          variants={fadeUp}>

          {QUICK_FILTERS.map((filter) =>
          <button
            key={filter}
            onClick={() => setActiveFilter(filter)}
            className={`px-4 py-1.5 text-sm font-medium rounded-full border transition-all ${activeFilter === filter ? 'bg-forest text-white border-forest' : 'bg-white dark:bg-[#122B1A] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-[#1F3D28] hover:border-forest hover:text-forest dark:hover:border-gold dark:hover:text-gold'}`}>

              {filter}
            </button>
          )}
        </motion.div>

        {/* Stats Row */}
        <motion.div
          className="flex flex-col sm:flex-row items-center justify-center gap-8 sm:gap-12"
          custom={4}
          initial="hidden"
          animate="visible"
          variants={fadeUp}>

          {[
          {
            icon: <ShieldCheckIcon className="w-5 h-5 text-forest" />,
            value: '2,847',
            label: 'Verified Listings',
            bg: 'bg-forest/10'
          },
          {
            icon: <CheckCircleIcon className="w-5 h-5 text-gold-dark" />,
            value: 'KES 0',
            label: 'Fraud Losses',
            bg: 'bg-gold/10'
          },
          {
            icon: <UsersIcon className="w-5 h-5 text-forest" />,
            value: '340+',
            label: 'Licensed Surveyors',
            bg: 'bg-forest/10'
          }].
          map((stat, i) =>
          <Fragment key={stat.label}>
              {i > 0 &&
            <div className="hidden sm:block w-px h-10 bg-gray-200 dark:bg-[#1F3D28]" />
            }
              <div className="flex items-center gap-3">
                <div
                className={`flex items-center justify-center w-10 h-10 rounded-full ${stat.bg}`}>

                  {stat.icon}
                </div>
                <div>
                  <div className="font-heading text-xl font-bold text-forest dark:text-gold">
                    {stat.value}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 font-body">
                    {stat.label}
                  </div>
                </div>
              </div>
            </Fragment>
          )}
        </motion.div>
      </div>
    </section>);

}