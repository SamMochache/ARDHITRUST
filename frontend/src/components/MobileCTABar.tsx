import React from 'react';
import { ShieldCheckIcon, ArrowRightIcon } from 'lucide-react';
export function MobileCTABar() {
  return (
    <div
      className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-forest dark:bg-[#071210] border-t border-forest-light dark:border-[#1F3D28] shadow-[0_-4px_20px_rgba(0,0,0,0.2)]"
      style={{
        paddingBottom: 'env(safe-area-inset-bottom)'
      }}>

      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-9 h-9 rounded-full bg-white/10">
            <ShieldCheckIcon className="w-5 h-5 text-gold" />
          </div>
          <div>
            <div className="text-white text-sm font-semibold font-body">
              Verify This Land
            </div>
            <div className="text-white/60 text-xs font-body">
              Official cadastral check
            </div>
          </div>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-gold rounded-xl font-bold text-sm text-forest shadow-md active:scale-95 transition-transform">
          <span>KES 500</span>
          <ArrowRightIcon className="w-4 h-4" />
        </button>
      </div>
    </div>);

}