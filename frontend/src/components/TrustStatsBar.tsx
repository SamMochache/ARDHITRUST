import React, { useEffect, useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  ShieldCheckIcon,
  TrendingUpIcon,
  ClockIcon,
  AwardIcon } from
'lucide-react';
function useCountUp(target: number, duration = 1500, start = false) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime: number | null = null;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, start]);
  return count;
}
const STATS = [
{
  icon: ShieldCheckIcon,
  value: 2847,
  suffix: '',
  label: 'Verified Listings'
},
{
  icon: TrendingUpIcon,
  value: 100,
  suffix: '%',
  label: 'Fraud-Free Record'
},
{
  icon: ClockIcon,
  value: 48,
  suffix: 'hr',
  label: 'Verification Time'
},
{
  icon: AwardIcon,
  value: 340,
  suffix: '+',
  label: 'Licensed Surveyors'
}];

function StatItem({
  icon: Icon,
  value,
  suffix,
  label,
  animate


}: (typeof STATS)[0] & {animate: boolean;}) {
  const count = useCountUp(value, 1500, animate);
  return (
    <div className="flex flex-col sm:flex-row items-center sm:items-start gap-3 lg:px-8 lg:first:pl-0 lg:last:pr-0">
      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 flex-shrink-0">
        <Icon className="w-5 h-5 text-gold" />
      </div>
      <div className="text-center sm:text-left">
        <div className="font-heading text-2xl font-bold text-white">
          {animate ? count : value}
          {suffix}
        </div>
        <div className="text-xs text-white/70 font-body mt-0.5">{label}</div>
      </div>
    </div>);

}
export function TrustStatsBar() {
  const ref = useRef(null);
  const isInView = useInView(ref, {
    once: true
  });
  return (
    <div ref={ref} className="bg-forest py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-0 lg:divide-x lg:divide-forest-light">
          {STATS.map((stat) =>
          <StatItem key={stat.label} {...stat} animate={isInView} />
          )}
        </div>
      </div>
    </div>);

}