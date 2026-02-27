import React from 'react';
import {
  ShieldCheckIcon,
  TwitterIcon,
  FacebookIcon,
  InstagramIcon,
  YoutubeIcon,
  ExternalLinkIcon } from
'lucide-react';
export function Footer() {
  return (
    <footer
      style={{
        backgroundColor: '#0A1A10',
        color: '#F0F7F1'
      }}>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
          {/* Column 1: Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{
                  backgroundColor: '#D4AF37'
                }}>

                <ShieldCheckIcon className="w-5 h-5 text-white" />
              </div>
              <span
                className="text-xl font-bold"
                style={{
                  fontFamily: 'Playfair Display, serif'
                }}>

                Ardhi
                <span
                  style={{
                    color: '#D4AF37'
                  }}>

                  Trust
                </span>
              </span>
            </div>
            <p
              className="text-sm leading-relaxed mb-6"
              style={{
                color: 'rgba(240,247,241,0.6)',
                fontFamily: 'Inter, sans-serif'
              }}>

              Kenya's Most Trusted Land Marketplace. Every listing verified.
              Every owner confirmed. No middlemen.
            </p>
            <div className="flex items-center gap-3">
              <a
                href="#"
                className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.08)'
                }}>

                <TwitterIcon
                  className="w-4 h-4"
                  style={{
                    color: '#D4AF37'
                  }} />

              </a>
              <a
                href="#"
                className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.08)'
                }}>

                <FacebookIcon
                  className="w-4 h-4"
                  style={{
                    color: '#D4AF37'
                  }} />

              </a>
              <a
                href="#"
                className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.08)'
                }}>

                <InstagramIcon
                  className="w-4 h-4"
                  style={{
                    color: '#D4AF37'
                  }} />

              </a>
              <a
                href="#"
                className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.08)'
                }}>

                <YoutubeIcon
                  className="w-4 h-4"
                  style={{
                    color: '#D4AF37'
                  }} />

              </a>
            </div>
          </div>

          {/* Column 2: For Buyers */}
          <div>
            <h4
              className="text-sm font-bold mb-4 uppercase tracking-wider"
              style={{
                color: '#D4AF37',
                fontFamily: 'Inter, sans-serif'
              }}>

              For Buyers
            </h4>
            <ul className="space-y-3">
              <li>
                <a
                  href="#listings"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Search Listings
                </a>
              </li>
              <li>
                <a
                  href="#verify"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Verify a Property
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Book a Valuer
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Due Diligence Reports
                </a>
              </li>
              <li>
                <a
                  href="#how-it-works"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  How It Works
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: For Sellers */}
          <div>
            <h4
              className="text-sm font-bold mb-4 uppercase tracking-wider"
              style={{
                color: '#D4AF37',
                fontFamily: 'Inter, sans-serif'
              }}>

              For Sellers
            </h4>
            <ul className="space-y-3">
              <li>
                <a
                  href="#sell"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  List Your Land
                </a>
              </li>
              <li>
                <a
                  href="#sell"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  KYC Verification
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Listing Pricing
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Seller Dashboard
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Verified Pro Upgrade
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Legal & Trust */}
          <div>
            <h4
              className="text-sm font-bold mb-4 uppercase tracking-wider"
              style={{
                color: '#D4AF37',
                fontFamily: 'Inter, sans-serif'
              }}>

              Legal & Trust
            </h4>
            <ul className="space-y-3">
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Terms of Service
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Privacy Policy
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="flex items-center gap-1.5 text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Ardhisasa Partnership
                  <ExternalLinkIcon className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="flex items-center gap-1.5 text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Ministry of Lands
                  <ExternalLinkIcon className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-sm transition-colors hover:opacity-80"
                  style={{
                    color: 'rgba(240,247,241,0.65)',
                    fontFamily: 'Inter, sans-serif'
                  }}>

                  Cookie Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div
          className="h-px mb-8"
          style={{
            backgroundColor: 'rgba(255,255,255,0.08)'
          }} />


        {/* Bottom bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p
            className="text-xs text-center sm:text-left"
            style={{
              color: 'rgba(240,247,241,0.4)',
              fontFamily: 'Inter, sans-serif'
            }}>

            © 2025 ArdhiTrust Ltd. Regulated under Kenya's Land Act 2012. All
            rights reserved.
          </p>
          <div className="flex items-center gap-3">
            <div
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
              style={{
                backgroundColor: 'rgba(27,67,50,0.6)',
                color: '#8FBF96',
                border: '1px solid rgba(27,67,50,0.8)'
              }}>

              🔒 SSL Secured
            </div>
            <div
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
              style={{
                backgroundColor: 'rgba(212,175,55,0.1)',
                color: '#D4AF37',
                border: '1px solid rgba(212,175,55,0.2)'
              }}>

              ✓ KRA Verified
            </div>
            <div
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
              style={{
                backgroundColor: 'rgba(27,67,50,0.6)',
                color: '#8FBF96',
                border: '1px solid rgba(27,67,50,0.8)'
              }}>

              🏛️ Land Act 2012
            </div>
          </div>
        </div>
      </div>
    </footer>);

}