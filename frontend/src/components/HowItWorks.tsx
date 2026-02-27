import React from 'react';
import { motion } from 'framer-motion';
import {
  SearchIcon,
  ShieldCheckIcon,
  MessageCircleIcon,
  ArrowRightIcon } from
'lucide-react';
const STEPS = [
{
  number: '01',
  icon: SearchIcon,
  title: 'Search & Filter',
  description:
  'Browse verified listings with Ardhisasa-backed data. Filter by location, size, type, and price. Every result is pre-screened.',
  highlight: 'No ghost listings'
},
{
  number: '02',
  icon: ShieldCheckIcon,
  title: 'Instant Verification',
  description:
  'We run cadastral checks via the Ministry of Lands API. See the LR Number, ownership history, and encumbrances in real time.',
  highlight: 'Ardhisasa-powered'
},
{
  number: '03',
  icon: MessageCircleIcon,
  title: 'Direct to Owner',
  description:
  'Message verified owners directly — no agents, no commission fees. Our Digital Escrow protects your payment throughout.',
  highlight: 'Zero middlemen'
}];

export function HowItWorks() {
  return (
    <section className="py-20 bg-forest relative overflow-hidden">
      {/* Subtle pattern overlay */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23D4AF37' fill-opacity='1' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E")`
        }} />


      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
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

          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 rounded-full mb-4 border border-gold/20">
            <ShieldCheckIcon className="w-3.5 h-3.5 text-gold" />
            <span className="text-xs font-semibold text-gold uppercase tracking-wider">
              How It Works
            </span>
          </div>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-white mb-4">
            Buying Land Has Never Been This Safe
          </h2>
          <p className="text-white/70 font-body text-base max-w-xl mx-auto">
            Three simple steps. Zero fraud risk. Full legal protection from
            search to title transfer.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-14">
          {STEPS.map((step, index) =>
          <motion.div
            key={step.number}
            className="relative"
            initial={{
              opacity: 0,
              x: -30
            }}
            whileInView={{
              opacity: 1,
              x: 0
            }}
            viewport={{
              once: true
            }}
            transition={{
              delay: index * 0.15,
              duration: 0.6
            }}>

              {/* Connector arrow (desktop) */}
              {index < 2 &&
            <div className="hidden md:flex absolute top-8 -right-4 z-10 items-center justify-center">
                  <ArrowRightIcon className="w-5 h-5 text-gold/40" />
                </div>
            }

              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-7 border border-white/10 hover:border-gold/30 transition-colors h-full">
                {/* Number + Icon */}
                <div className="flex items-center gap-4 mb-5">
                  <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-gold/20 border border-gold/30">
                    <step.icon className="w-6 h-6 text-gold" />
                  </div>
                  <span className="font-heading text-4xl font-bold text-white/20">
                    {step.number}
                  </span>
                </div>

                <h3 className="font-heading text-xl font-bold text-white mb-3">
                  {step.title}
                </h3>
                <p className="text-white/70 font-body text-sm leading-relaxed mb-4">
                  {step.description}
                </p>

                <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-gold/20 rounded-full border border-gold/30">
                  <div className="w-1.5 h-1.5 rounded-full bg-gold" />
                  <span className="text-xs font-semibold text-gold">
                    {step.highlight}
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* CTA */}
        <motion.div
          className="text-center"
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
            delay: 0.4,
            duration: 0.5
          }}>

          <button className="inline-flex items-center gap-2 px-8 py-4 bg-gold text-forest font-bold rounded-xl hover:bg-gold-light transition-colors shadow-lg text-sm">
            Start Searching Verified Land
            <ArrowRightIcon className="w-4 h-4" />
          </button>
          <p className="text-white/50 text-xs font-body mt-3">
            No registration required to browse
          </p>
        </motion.div>
      </div>
    </section>);

}