import React from 'react';
import { motion } from 'framer-motion';
import {
  SearchIcon,
  FileTextIcon,
  AwardIcon,
  HomeIcon,
  LockIcon,
  ArrowRightIcon,
  CheckIcon } from
'lucide-react';
interface Step {
  id: number;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'completed' | 'active' | 'pending';
  timeline: string;
}
const STEPS: Step[] = [
{
  id: 1,
  name: 'Search Certificate',
  description:
  'Official search from Ministry of Lands confirms ownership & encumbrances',
  icon: <SearchIcon className="w-5 h-5" />,
  status: 'completed',
  timeline: '1–3 days'
},
{
  id: 2,
  name: 'Sale Agreement',
  description: 'Legally binding sale agreement drafted and signed digitally',
  icon: <FileTextIcon className="w-5 h-5" />,
  status: 'active',
  timeline: '3–7 days'
},
{
  id: 3,
  name: 'Land Board Approval',
  description: 'County Land Board reviews and approves the transfer',
  icon: <AwardIcon className="w-5 h-5" />,
  status: 'pending',
  timeline: '14–30 days'
},
{
  id: 4,
  name: 'Title Transfer',
  description:
  'Title deed transferred to your name. Funds released to seller',
  icon: <HomeIcon className="w-5 h-5" />,
  status: 'pending',
  timeline: '7–14 days'
}];

export function EscrowTracker() {
  return (
    <section className="py-20 bg-cream dark:bg-[#0F2318]" id="how-it-works">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-forest/10 dark:bg-forest/20 rounded-full mb-4">
            <LockIcon className="w-3.5 h-3.5 text-forest dark:text-gold" />
            <span className="text-xs font-semibold text-forest dark:text-gold uppercase tracking-wider">
              Digital Escrow
            </span>
          </div>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-3">
            Your Legal Journey, Simplified
          </h2>
          <p className="text-gray-500 dark:text-gray-400 font-body text-base max-w-xl mx-auto">
            Your money is held securely until every legal step is complete
          </p>
        </div>

        {/* Desktop */}
        <div className="hidden md:block relative mb-12">
          <div className="absolute top-8 left-[12.5%] right-[12.5%] h-0.5 bg-gray-200 dark:bg-[#1F3D28] z-0">
            <div
              className="h-full bg-gold transition-all duration-700"
              style={{
                width: '33%'
              }} />

          </div>
          <div className="relative z-10 grid grid-cols-4 gap-4">
            {STEPS.map((step, index) =>
            <DesktopStep key={step.id} step={step} index={index} />
            )}
          </div>
        </div>

        {/* Mobile */}
        <div className="md:hidden space-y-4 mb-12">
          {STEPS.map((step, index) =>
          <MobileStep key={step.id} step={step} index={index} />
          )}
        </div>

        {/* Security Note */}
        <div className="flex flex-col sm:flex-row items-center gap-4 p-6 bg-white dark:bg-[#122B1A] rounded-2xl border border-forest/10 dark:border-[#1F3D28] shadow-sm mb-8">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-forest/10 flex-shrink-0">
            <LockIcon className="w-6 h-6 text-forest dark:text-gold" />
          </div>
          <div className="text-center sm:text-left">
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200 font-body">
              Your funds are held in a regulated escrow account until Title
              Transfer is complete
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 font-body">
              Regulated by the Central Bank of Kenya · FSCA Compliant
            </p>
          </div>
        </div>

        <div className="flex justify-center">
          <button className="flex items-center gap-2 px-8 py-4 bg-forest text-white font-semibold rounded-xl hover:bg-forest-light transition-colors shadow-lg text-sm">
            <LockIcon className="w-4 h-4" />
            Start Secure Purchase
            <ArrowRightIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>);

}
function DesktopStep({ step, index }: {step: Step;index: number;}) {
  const isCompleted = step.status === 'completed';
  const isActive = step.status === 'active';
  const isPending = step.status === 'pending';
  return (
    <motion.div
      className="flex flex-col items-center text-center"
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
        delay: index * 0.15,
        duration: 0.5
      }}>

      <div className="relative mb-4">
        {isActive &&
        <motion.div
          className="absolute inset-0 rounded-full bg-forest/20"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.6, 0, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut'
          }} />

        }
        <div
          className={`relative w-16 h-16 rounded-full flex items-center justify-center border-2 transition-all ${isCompleted ? 'bg-forest border-forest text-white' : isActive ? 'bg-forest border-gold text-white shadow-gold' : 'bg-white dark:bg-[#122B1A] border-gray-200 dark:border-[#1F3D28] text-gray-400'}`}>

          {isCompleted ?
          <CheckIcon className="w-6 h-6" /> :

          <div
            className={
            isActive ? 'text-white' : 'text-gray-400 dark:text-gray-500'
            }>

              {step.icon}
            </div>
          }
          <div
            className={`absolute -top-1 -right-1 w-5 h-5 rounded-full text-xs font-bold flex items-center justify-center ${isCompleted || isActive ? 'bg-gold text-white' : 'bg-gray-200 dark:bg-[#1F3D28] text-gray-500 dark:text-gray-400'}`}>

            {step.id}
          </div>
        </div>
      </div>
      <h3
        className={`font-heading text-sm font-bold mb-1.5 ${isPending ? 'text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-white'}`}>

        {step.name}
      </h3>
      <p
        className={`text-xs font-body leading-relaxed mb-2 ${isPending ? 'text-gray-300 dark:text-gray-600' : 'text-gray-500 dark:text-gray-400'}`}>

        {step.description}
      </p>
      <span
        className={`text-xs font-medium ${isPending ? 'text-gray-300 dark:text-gray-600' : 'text-forest dark:text-gold'}`}>

        ⏱ {step.timeline}
      </span>
      {isActive &&
      <div className="mt-2 px-2.5 py-0.5 bg-gold/10 rounded-full">
          <span className="text-xs font-semibold text-gold-dark">
            In Progress
          </span>
        </div>
      }
    </motion.div>);

}
function MobileStep({ step, index }: {step: Step;index: number;}) {
  const isCompleted = step.status === 'completed';
  const isActive = step.status === 'active';
  const isPending = step.status === 'pending';
  return (
    <motion.div
      className="flex gap-4"
      initial={{
        opacity: 0,
        x: -20
      }}
      whileInView={{
        opacity: 1,
        x: 0
      }}
      viewport={{
        once: true
      }}
      transition={{
        delay: index * 0.1,
        duration: 0.4
      }}>

      <div className="flex flex-col items-center">
        <div className="relative">
          {isActive &&
          <motion.div
            className="absolute inset-0 rounded-full bg-forest/20"
            animate={{
              scale: [1, 1.6, 1],
              opacity: [0.5, 0, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity
            }} />

          }
          <div
            className={`relative w-12 h-12 rounded-full flex items-center justify-center border-2 ${isCompleted ? 'bg-forest border-forest text-white' : isActive ? 'bg-forest border-gold text-white' : 'bg-white dark:bg-[#122B1A] border-gray-200 dark:border-[#1F3D28] text-gray-400'}`}>

            {isCompleted ? <CheckIcon className="w-5 h-5" /> : step.icon}
            <div
              className={`absolute -top-1 -right-1 w-4 h-4 rounded-full text-xs font-bold flex items-center justify-center ${isCompleted || isActive ? 'bg-gold text-white' : 'bg-gray-200 dark:bg-[#1F3D28] text-gray-500'}`}>

              {step.id}
            </div>
          </div>
        </div>
        {index < 3 &&
        <div
          className={`w-0.5 h-8 mt-1 ${isCompleted ? 'bg-gold' : 'bg-gray-200 dark:bg-[#1F3D28]'}`} />

        }
      </div>
      <div className="pb-6 flex-1">
        <div className="flex items-center gap-2 mb-1">
          <h3
            className={`font-heading text-sm font-bold ${isPending ? 'text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-white'}`}>

            {step.name}
          </h3>
          {isActive &&
          <span className="px-2 py-0.5 bg-gold/10 rounded-full text-xs font-semibold text-gold-dark">
              In Progress
            </span>
          }
        </div>
        <p
          className={`text-xs font-body leading-relaxed ${isPending ? 'text-gray-300 dark:text-gray-600' : 'text-gray-500 dark:text-gray-400'}`}>

          {step.description}
        </p>
        <span
          className={`text-xs font-medium mt-1 block ${isPending ? 'text-gray-300 dark:text-gray-600' : 'text-forest dark:text-gold'}`}>

          ⏱ {step.timeline}
        </span>
      </div>
    </motion.div>);

}