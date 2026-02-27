import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  StarIcon,
  ShieldCheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon } from
'lucide-react';
const TESTIMONIALS = [
{
  name: 'James Mwangi',
  location: 'Nairobi',
  initials: 'JM',
  color: 'bg-forest',
  rating: 5,
  quote:
  "I was about to pay KES 4.5M for land that turned out to have a caveat. ArdhiTrust's verification caught it in 2 hours. This platform literally saved my life savings.",
  property: 'Residential Plot, Karen',
  date: '3 weeks ago'
},
{
  name: 'Wanjiru Kamau',
  location: 'Nakuru',
  initials: 'WK',
  color: 'bg-amber-700',
  rating: 5,
  quote:
  'The Digital Escrow gave me so much peace of mind. I could see every step of the transfer process in real time. No more wondering if the agent is lying to you.',
  property: 'Agricultural Land, Nakuru',
  date: '1 month ago'
},
{
  name: 'David Ochieng',
  location: 'Kisumu',
  initials: 'DO',
  color: 'bg-blue-800',
  rating: 5,
  quote:
  'Bought 5 acres directly from the owner. No agent fees, no commission. The Due Diligence Report for KES 500 was the best investment I made — it showed a clean title.',
  property: 'Farm Land, Kisumu',
  date: '2 months ago'
},
{
  name: 'Fatuma Hassan',
  location: 'Mombasa',
  initials: 'FH',
  color: 'bg-teal-700',
  rating: 5,
  quote:
  "As a woman buying land alone, I was worried about being taken advantage of. ArdhiTrust's verification system and direct owner messaging made me feel completely protected.",
  property: 'Beach Plot, Diani',
  date: '6 weeks ago'
}];

function StarRating({ count }: {count: number;}) {
  return (
    <div className="flex gap-0.5">
      {Array.from({
        length: count
      }).map((_, i) =>
      <StarIcon key={i} className="w-4 h-4 text-gold fill-gold" />
      )}
    </div>);

}
export function Testimonials() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  useEffect(() => {
    if (!isAutoPlaying) return;
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % TESTIMONIALS.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [isAutoPlaying]);
  const prev = () => {
    setIsAutoPlaying(false);
    setActiveIndex((i) => (i - 1 + TESTIMONIALS.length) % TESTIMONIALS.length);
  };
  const next = () => {
    setIsAutoPlaying(false);
    setActiveIndex((i) => (i + 1) % TESTIMONIALS.length);
  };
  return (
    <section className="py-20 bg-cream dark:bg-[#0F2318]">
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
            <ShieldCheckIcon className="w-3.5 h-3.5 text-forest dark:text-gold" />
            <span className="text-xs font-semibold text-forest dark:text-gold uppercase tracking-wider">
              Verified Buyers
            </span>
          </div>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-3">
            Real People. Real Land. Zero Fraud.
          </h2>
          <p className="text-gray-500 dark:text-gray-400 font-body text-base max-w-xl mx-auto">
            Join thousands of Kenyans who bought land safely through ArdhiTrust
          </p>
        </motion.div>

        {/* Desktop Grid */}
        <div className="hidden md:grid grid-cols-2 lg:grid-cols-4 gap-5">
          {TESTIMONIALS.map((t, index) =>
          <motion.div
            key={t.name}
            className="bg-white dark:bg-[#122B1A] rounded-2xl p-6 border border-gray-100 dark:border-[#1F3D28] flex flex-col"
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
              delay: index * 0.1,
              duration: 0.5
            }}>

              <div className="flex items-center gap-3 mb-4">
                <div
                className={`w-10 h-10 rounded-full ${t.color} flex items-center justify-center flex-shrink-0`}>

                  <span className="text-sm font-bold text-white">
                    {t.initials}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white font-body">
                    {t.name}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 font-body">
                    {t.location}
                  </p>
                </div>
              </div>
              <StarRating count={t.rating} />
              <p className="text-sm text-gray-600 dark:text-gray-400 font-body leading-relaxed mt-3 flex-1 italic">
                "{t.quote}"
              </p>
              <div className="mt-4 pt-4 border-t border-gray-100 dark:border-[#1F3D28]">
                <div className="flex items-center gap-1.5">
                  <ShieldCheckIcon className="w-3 h-3 text-forest dark:text-gold" />
                  <span className="text-xs text-forest dark:text-gold font-semibold font-body">
                    Verified Buyer
                  </span>
                </div>
                <p className="text-xs text-gray-400 dark:text-gray-500 font-body mt-0.5">
                  {t.property}
                </p>
              </div>
            </motion.div>
          )}
        </div>

        {/* Mobile Carousel */}
        <div className="md:hidden">
          <div className="relative overflow-hidden rounded-2xl">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeIndex}
                initial={{
                  opacity: 0,
                  x: 40
                }}
                animate={{
                  opacity: 1,
                  x: 0
                }}
                exit={{
                  opacity: 0,
                  x: -40
                }}
                transition={{
                  duration: 0.35
                }}
                className="bg-white dark:bg-[#122B1A] rounded-2xl p-6 border border-gray-100 dark:border-[#1F3D28]">

                {(() => {
                  const t = TESTIMONIALS[activeIndex];
                  return (
                    <>
                      <div className="flex items-center gap-3 mb-4">
                        <div
                          className={`w-12 h-12 rounded-full ${t.color} flex items-center justify-center`}>

                          <span className="text-sm font-bold text-white">
                            {t.initials}
                          </span>
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900 dark:text-white font-body">
                            {t.name}
                          </p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 font-body">
                            {t.location} · {t.date}
                          </p>
                        </div>
                      </div>
                      <StarRating count={t.rating} />
                      <p className="text-sm text-gray-600 dark:text-gray-400 font-body leading-relaxed mt-4 italic">
                        "{t.quote}"
                      </p>
                      <div className="mt-5 pt-4 border-t border-gray-100 dark:border-[#1F3D28] flex items-center gap-1.5">
                        <ShieldCheckIcon className="w-3.5 h-3.5 text-forest dark:text-gold" />
                        <span className="text-xs text-forest dark:text-gold font-semibold font-body">
                          Verified Buyer · {t.property}
                        </span>
                      </div>
                    </>);

                })()}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Carousel Controls */}
          <div className="flex items-center justify-center gap-4 mt-5">
            <button
              onClick={prev}
              className="flex items-center justify-center w-9 h-9 rounded-full border border-gray-200 dark:border-[#1F3D28] bg-white dark:bg-[#122B1A] hover:border-forest dark:hover:border-gold transition-colors">

              <ChevronLeftIcon className="w-4 h-4 text-gray-600 dark:text-gray-300" />
            </button>
            <div className="flex gap-2">
              {TESTIMONIALS.map((_, i) =>
              <button
                key={i}
                onClick={() => {
                  setIsAutoPlaying(false);
                  setActiveIndex(i);
                }}
                className={`w-2 h-2 rounded-full transition-all ${i === activeIndex ? 'bg-forest dark:bg-gold w-5' : 'bg-gray-200 dark:bg-[#1F3D28]'}`} />

              )}
            </div>
            <button
              onClick={next}
              className="flex items-center justify-center w-9 h-9 rounded-full border border-gray-200 dark:border-[#1F3D28] bg-white dark:bg-[#122B1A] hover:border-forest dark:hover:border-gold transition-colors">

              <ChevronRightIcon className="w-4 h-4 text-gray-600 dark:text-gray-300" />
            </button>
          </div>
        </div>
      </div>
    </section>);

}