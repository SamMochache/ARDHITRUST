import React from 'react';
import { Navbar } from '../components/Navbar';
import { HeroSection } from '../components/HeroSection';
import { TrustStatsBar } from '../components/TrustStatsBar';
import { PropertyGrid } from '../components/PropertyGrid';
import { EscrowTracker } from '../components/EscrowTracker';
import { HowItWorks } from '../components/HowItWorks';
import { ValueAddServices } from '../components/ValueAddServices';
import { SellerOnboarding } from '../components/SellerOnboarding';
import { Testimonials } from '../components/Testimonials';
import { MobileCTABar } from '../components/MobileCTABar';
import {
  ShieldCheckIcon,
  FileTextIcon,
  PhoneIcon,
  MailIcon,
  TwitterIcon,
  FacebookIcon,
  InstagramIcon } from
'lucide-react';
export function Home() {
  return (
    <div className="min-h-screen w-full bg-white dark:bg-[#0A1A10] font-body transition-colors duration-300">
      <Navbar />
      <main>
        <HeroSection />
        <TrustStatsBar />
        <PropertyGrid />
        <EscrowTracker />
        <HowItWorks />
        <ValueAddServices />
        <SellerOnboarding />
        <Testimonials />
        <TrustBanner />
      </main>
      <Footer />
      <MobileCTABar />
    </div>);

}
function TrustBanner() {
  return (
    <section className="py-16 bg-forest relative overflow-hidden">
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23D4AF37' fill-opacity='1' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E")`
        }} />

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="flex justify-center mb-6">
          <div className="flex items-center justify-center w-16 h-16 rounded-full bg-white/10 border border-gold/30">
            <ShieldCheckIcon className="w-8 h-8 text-gold" />
          </div>
        </div>
        <h2 className="font-heading text-3xl sm:text-4xl font-bold text-white mb-4">
          Kenya's Most Trusted Land Marketplace
        </h2>
        <p className="text-white/70 font-body text-base max-w-2xl mx-auto mb-8 leading-relaxed">
          Every listing on ArdhiTrust is independently verified by licensed
          surveyors and protected by our Digital Escrow system. Buy with
          confidence.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="px-8 py-3.5 bg-gold text-forest font-bold rounded-xl hover:bg-gold-light transition-colors shadow-lg text-sm">
            Browse Verified Listings
          </button>
          <button className="px-8 py-3.5 bg-white/10 text-white font-semibold rounded-xl hover:bg-white/20 transition-colors border border-white/20 text-sm">
            How Verification Works
          </button>
        </div>
      </div>
    </section>);

}
function Footer() {
  return (
    <footer className="bg-[#0A1A10] text-white py-14">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-10">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-forest">
                <ShieldCheckIcon className="w-5 h-5 text-gold" />
              </div>
              <span className="font-heading text-xl font-bold text-white">
                ArdhiTrust
              </span>
            </div>
            <p className="text-gray-400 text-sm font-body leading-relaxed mb-5">
              Kenya's verification-first land marketplace. No agents. No fraud.
              Just trust.
            </p>
            <div className="flex gap-3 mb-5">
              {[TwitterIcon, FacebookIcon, InstagramIcon].map((Icon, i) =>
              <a
                key={i}
                href="#"
                className="flex items-center justify-center w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 transition-colors">

                  <Icon className="w-4 h-4 text-gray-400" />
                </a>
              )}
            </div>
            {/* Trust Badges */}
            <div className="flex flex-wrap gap-2">
              {['SSL Secured', 'KRA Verified', 'Land Act 2012'].map((badge) =>
              <span
                key={badge}
                className="px-2.5 py-1 text-xs font-medium text-gold border border-gold/30 rounded-full bg-gold/5">

                  {badge}
                </span>
              )}
            </div>
          </div>

          {/* For Buyers */}
          <div>
            <h4 className="font-heading text-sm font-semibold text-white mb-4 uppercase tracking-wider">
              For Buyers
            </h4>
            <ul className="space-y-2.5">
              {[
              'Search Listings',
              'Verify a Property',
              'Book a Valuer',
              'Due Diligence Reports',
              'Digital Escrow'].
              map((link) =>
              <li key={link}>
                  <a
                  href="#"
                  className="text-sm text-gray-400 hover:text-gold transition-colors font-body">

                    {link}
                  </a>
                </li>
              )}
            </ul>
          </div>

          {/* For Sellers */}
          <div>
            <h4 className="font-heading text-sm font-semibold text-white mb-4 uppercase tracking-wider">
              For Sellers
            </h4>
            <ul className="space-y-2.5">
              {[
              'List Your Land',
              'KYC Verification',
              'Verified Pro Listing',
              'Seller Dashboard',
              'Pricing'].
              map((link) =>
              <li key={link}>
                  <a
                  href="#"
                  className="text-sm text-gray-400 hover:text-gold transition-colors font-body">

                    {link}
                  </a>
                </li>
              )}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-heading text-sm font-semibold text-white mb-4 uppercase tracking-wider">
              Contact
            </h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2.5">
                <PhoneIcon className="w-4 h-4 text-gold flex-shrink-0" />
                <span className="text-sm text-gray-400 font-body">
                  +254 700 000 000
                </span>
              </li>
              <li className="flex items-center gap-2.5">
                <MailIcon className="w-4 h-4 text-gold flex-shrink-0" />
                <span className="text-sm text-gray-400 font-body">
                  hello@ardhitrust.co.ke
                </span>
              </li>
              <li className="flex items-start gap-2.5 mt-2">
                <FileTextIcon className="w-4 h-4 text-gold flex-shrink-0 mt-0.5" />
                <span className="text-sm text-gray-400 font-body">
                  Westlands Business Park
                  <br />
                  Nairobi, Kenya
                </span>
              </li>
            </ul>
            <div className="mt-5 space-y-2">
              {[
              'Privacy Policy',
              'Terms of Service',
              'Ardhisasa Partnership'].
              map((link) =>
              <a
                key={link}
                href="#"
                className="block text-xs text-gray-500 hover:text-gray-300 transition-colors font-body">

                  {link}
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-gray-500 font-body">
            © 2025 ArdhiTrust Ltd. All rights reserved. Regulated under Kenya's
            Land Act 2012.
          </p>
          <p className="text-xs text-gray-600 font-body">
            Ardhisasa API Partner · Ministry of Lands Kenya
          </p>
        </div>
      </div>
    </footer>);

}