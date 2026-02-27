import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheckIcon,
  MenuIcon,
  XIcon,
  SunIcon,
  MoonIcon } from
'lucide-react';
import { useTheme } from '../context/ThemeContext';

function scrollToSell() {
  const el = document.getElementById('sell');
  if (el) el.scrollIntoView({ behavior: 'smooth' });
}

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { theme, toggleTheme } = useTheme();
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  return (
    <nav
      className={`sticky top-0 z-50 transition-all duration-300 ${isScrolled ? 'shadow-lg' : 'shadow-sm'} bg-white dark:bg-[#071210] border-b border-gray-100 dark:border-[#1F3D28]`}>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2 cursor-pointer">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-forest">
              <ShieldCheckIcon className="w-5 h-5 text-gold" />
            </div>
            <span className="font-heading text-xl font-bold text-forest dark:text-white tracking-tight">
              ArdhiTrust
            </span>
          </div>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-8">
            {[
              { label: 'Browse Land', href: '#listings' },
              { label: 'How It Works', href: '#how-it-works' },
              { label: 'Verify Land', href: '#' },
            ].map(({ label, href }) =>
            <a
              key={label}
              href={href}
              className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-forest dark:hover:text-gold transition-colors">
              {label}
            </a>
            )}
          </div>

          {/* Desktop Right: Theme Toggle + CTA */}
          <div className="hidden md:flex items-center gap-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="relative flex items-center justify-center w-10 h-10 rounded-xl border border-gray-200 dark:border-[#1F3D28] bg-gray-50 dark:bg-[#0F2318] hover:border-forest dark:hover:border-gold transition-all"
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>

              <AnimatePresence mode="wait">
                {theme === 'light' ?
                <motion.div
                  key="moon"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                  transition={{ duration: 0.2 }}>
                    <MoonIcon className="w-4 h-4 text-forest" />
                  </motion.div> :
                <motion.div
                  key="sun"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                  transition={{ duration: 0.2 }}>
                    <SunIcon className="w-4 h-4 text-gold" />
                  </motion.div>
                }
              </AnimatePresence>
            </button>

            <button
              onClick={scrollToSell}
              className="px-5 py-2 text-sm font-semibold text-white bg-forest rounded-lg hover:bg-forest-light transition-colors">
              List Property
            </button>
          </div>

          {/* Mobile Right: Theme Toggle + Hamburger */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 dark:border-[#1F3D28] bg-gray-50 dark:bg-[#0F2318]"
              aria-label="Toggle theme">

              <AnimatePresence mode="wait">
                {theme === 'light' ?
                <motion.div
                  key="moon-mobile"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                  transition={{ duration: 0.2 }}>
                    <MoonIcon className="w-4 h-4 text-forest" />
                  </motion.div> :
                <motion.div
                  key="sun-mobile"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                  transition={{ duration: 0.2 }}>
                    <SunIcon className="w-4 h-4 text-gold" />
                  </motion.div>
                }
              </AnimatePresence>
            </button>

            <button
              className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#1F3D28] transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="Toggle menu">
              {isMenuOpen ?
              <XIcon className="w-5 h-5" /> :
              <MenuIcon className="w-5 h-5" />
              }
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen &&
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
          className="md:hidden bg-white dark:bg-[#071210] border-t border-gray-100 dark:border-[#1F3D28] px-4 py-4 space-y-3 overflow-hidden">

          {[
            { label: 'Browse Land', href: '#listings' },
            { label: 'How It Works', href: '#how-it-works' },
            { label: 'Verify Land', href: '#' },
            { label: 'Sign In', href: '#' },
          ].map(({ label, href }) =>
          <a
            key={label}
            href={href}
            className="block py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-forest dark:hover:text-gold"
            onClick={() => setIsMenuOpen(false)}>
            {label}
          </a>
          )}
          <button
            onClick={() => { setIsMenuOpen(false); scrollToSell(); }}
            className="w-full mt-2 px-5 py-2.5 text-sm font-semibold text-white bg-forest rounded-lg hover:bg-forest-light transition-colors">
            List Property
          </button>
        </motion.div>
        }
      </AnimatePresence>
    </nav>);
}