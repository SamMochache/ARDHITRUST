import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart2Icon,
  RulerIcon,
  FileTextIcon,
  CheckIcon,
  ArrowRightIcon,
  StarIcon } from
'lucide-react';
const SERVICES = [
{
  icon: BarChart2Icon,
  title: 'Book a Licensed Valuer',
  subtitle: 'Get 3 competitive quotes in 24 hours',
  description:
  'Registered valuers bid on your request. Compare quotes from RICS-certified professionals before you commit.',
  features: [
  '3 quotes in 24 hours',
  'RICS-certified valuers',
  'Digital valuation report',
  'Bank-accepted certificates'],

  cta: 'Request Valuation',
  price: 'Free to request',
  variant: 'outline' as const,
  badge: null
},
{
  icon: RulerIcon,
  title: 'Book a Surveyor',
  subtitle: 'Confirm exact boundaries before you buy',
  description:
  'Our network of licensed surveyors will physically verify the land boundaries match the title deed.',
  features: [
  'GPS boundary marking',
  'Beacon placement',
  'Survey report PDF',
  'Ministry of Lands filing'],

  cta: 'Book Survey',
  price: 'From KES 8,000',
  variant: 'outline' as const,
  badge: null
},
{
  icon: FileTextIcon,
  title: 'Due Diligence Report',
  subtitle: 'Everything you need in one official PDF',
  description:
  'Official search + ownership history + encumbrances + caveats + rates clearance — all in one downloadable report.',
  features: [
  'Official Ministry search',
  'Ownership chain history',
  'Encumbrances & caveats',
  'Rates & rent clearance'],

  cta: 'Buy Report',
  price: 'KES 500',
  variant: 'featured' as const,
  badge: 'Most Popular'
}];

export function ValueAddServices() {
  const [loadingIndex, setLoadingIndex] = useState<number | null>(null);
  const handleClick = (index: number) => {
    setLoadingIndex(index);
    setTimeout(() => setLoadingIndex(null), 2000);
  };
  return (
    <section className="py-20 bg-white dark:bg-[#0A1A10]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-14"
          initial={{
            opacity: 0,
            y: 20
          }}
          whileInView={{
            opacity: 1,
            y: 0
          }}
          viewport={{
            once: true
          }}
          transition={{
            duration: 0.6
          }}>

          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-forest/10 dark:bg-forest/20 rounded-full mb-4">
            <StarIcon className="w-3.5 h-3.5 text-forest dark:text-gold" />
            <span className="text-xs font-semibold text-forest dark:text-gold uppercase tracking-wider">
              Value-Add Services
            </span>
          </div>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Protect Your Investment
          </h2>
          <p className="text-gray-500 dark:text-gray-400 font-body text-base max-w-xl mx-auto">
            Professional services at your fingertips. One click to book,
            transparent pricing, no surprises.
          </p>
        </motion.div>

        {/* Service Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SERVICES.map((service, index) =>
          <motion.div
            key={service.title}
            className={`relative rounded-2xl p-7 flex flex-col border-2 transition-all ${service.variant === 'featured' ? 'bg-forest dark:bg-forest border-gold shadow-gold' : 'bg-white dark:bg-[#122B1A] border-gray-100 dark:border-[#1F3D28] hover:border-forest dark:hover:border-gold'}`}
            initial={{
              opacity: 0,
              y: 24
            }}
            whileInView={{
              opacity: 1,
              y: 0
            }}
            viewport={{
              once: true
            }}
            transition={{
              delay: index * 0.1,
              duration: 0.5
            }}
            whileHover={{
              y: -4
            }}>

              {/* Badge */}
              {service.badge &&
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <div className="px-4 py-1 bg-gold rounded-full text-xs font-bold text-forest shadow-md">
                    {service.badge}
                  </div>
                </div>
            }

              {/* Icon */}
              <div
              className={`flex items-center justify-center w-12 h-12 rounded-xl mb-5 ${service.variant === 'featured' ? 'bg-gold/20 border border-gold/30' : 'bg-forest/10 dark:bg-forest/20'}`}>

                <service.icon
                className={`w-6 h-6 ${service.variant === 'featured' ? 'text-gold' : 'text-forest dark:text-gold'}`} />

              </div>

              <h3
              className={`font-heading text-xl font-bold mb-1 ${service.variant === 'featured' ? 'text-white' : 'text-gray-900 dark:text-white'}`}>

                {service.title}
              </h3>
              <p
              className={`text-xs font-semibold mb-3 ${service.variant === 'featured' ? 'text-gold' : 'text-forest dark:text-gold'}`}>

                {service.subtitle}
              </p>
              <p
              className={`text-sm font-body leading-relaxed mb-5 ${service.variant === 'featured' ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'}`}>

                {service.description}
              </p>

              {/* Features */}
              <ul className="space-y-2 mb-6 flex-1">
                {service.features.map((feature) =>
              <li key={feature} className="flex items-center gap-2">
                    <div
                  className={`flex items-center justify-center w-4 h-4 rounded-full flex-shrink-0 ${service.variant === 'featured' ? 'bg-gold/20' : 'bg-forest/10 dark:bg-forest/20'}`}>

                      <CheckIcon
                    className={`w-2.5 h-2.5 ${service.variant === 'featured' ? 'text-gold' : 'text-forest dark:text-gold'}`} />

                    </div>
                    <span
                  className={`text-xs font-body ${service.variant === 'featured' ? 'text-white/80' : 'text-gray-600 dark:text-gray-400'}`}>

                      {feature}
                    </span>
                  </li>
              )}
              </ul>

              {/* Price + CTA */}
              <div>
                <div
                className={`font-heading text-2xl font-bold mb-3 ${service.variant === 'featured' ? 'text-gold' : 'text-forest dark:text-gold'}`}>

                  {service.price}
                </div>
                <button
                onClick={() => handleClick(index)}
                className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all ${service.variant === 'featured' ? 'bg-gold text-forest hover:bg-gold-light active:scale-95' : 'bg-forest dark:bg-gold text-white dark:text-forest hover:bg-forest-light dark:hover:bg-gold-light active:scale-95'}`}>

                  {loadingIndex === index ?
                <motion.div
                  className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
                  animate={{
                    rotate: 360
                  }}
                  transition={{
                    duration: 0.8,
                    repeat: Infinity,
                    ease: 'linear'
                  }} /> :


                <>
                      {service.cta}
                      <ArrowRightIcon className="w-4 h-4" />
                    </>
                }
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </section>);

}