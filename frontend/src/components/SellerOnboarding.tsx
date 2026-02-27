import { useState, Fragment } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UploadIcon,
  KeyIcon,
  MapIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  ShieldCheckIcon,
  UserIcon,
  FileTextIcon } from
'lucide-react';
const STEPS = [
{
  id: 1,
  icon: UserIcon,
  title: 'National ID Scan',
  subtitle: 'Upload your Kenya National ID (both sides)',
  description:
  'We verify your identity against the IPRS database to eliminate ghost agents.'
},
{
  id: 2,
  icon: KeyIcon,
  title: 'KRA PIN Verification',
  subtitle: 'Enter your KRA PIN for tax compliance check',
  description:
  'Required by Kenya Revenue Authority for all property transactions above KES 3M.'
},
{
  id: 3,
  icon: MapIcon,
  title: 'Cadastral Check',
  subtitle: 'Enter your LR Number for Ardhisasa verification',
  description:
  'We confirm your ownership via the Ministry of Lands API before your listing goes live.'
}];

export function SellerOnboarding() {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [isChecking, setIsChecking] = useState(false);
  const [kraPin, setKraPin] = useState('');
  const [lrNumber, setLrNumber] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const progressPct = completedSteps.length / 3 * 100;
  const handleNext = () => {
    if (currentStep === 2) {
      setIsChecking(true);
      setTimeout(() => {
        setIsChecking(false);
        setCompletedSteps([0, 1, 2]);
        setCurrentStep(3);
      }, 2000);
      return;
    }
    setIsChecking(true);
    setTimeout(() => {
      setIsChecking(false);
      setCompletedSteps((prev) => [...prev, currentStep]);
      setCurrentStep((prev) => prev + 1);
    }, 1500);
  };
  return (
    <section id="sell" className="py-20 bg-cream dark:bg-[#0F2318]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}>

          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-forest/10 dark:bg-forest/20 rounded-full mb-4">
            <ShieldCheckIcon className="w-3.5 h-3.5 text-forest dark:text-gold" />
            <span className="text-xs font-semibold text-forest dark:text-gold uppercase tracking-wider">
              For Sellers
            </span>
          </div>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-3">
            List Your Land in 3 Steps
          </h2>
          <p className="text-gray-500 dark:text-gray-400 font-body text-base max-w-lg mx-auto">
            Our KYC process eliminates fraud and gives buyers confidence.
            Verified listings sell 3× faster.
          </p>
        </motion.div>

        <div className="bg-white dark:bg-[#122B1A] rounded-3xl border border-gray-100 dark:border-[#1F3D28] shadow-card overflow-hidden">
          {/* Progress Bar */}
          <div className="h-1.5 bg-gray-100 dark:bg-[#1F3D28]">
            <motion.div
              className="h-full bg-gold"
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }} />
          </div>

          <div className="p-8">
            {/* Step Indicators */}
            <div className="flex items-center justify-between mb-10">
              {STEPS.map((step, index) => {
                const isCompleted = completedSteps.includes(index);
                const isActive = currentStep === index;
                return (
                  <Fragment key={step.id}>
                    <div className="flex flex-col items-center gap-2">
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${isCompleted ? 'bg-forest border-forest' : isActive ? 'bg-white dark:bg-[#0F2318] border-forest dark:border-gold shadow-gold' : 'bg-gray-50 dark:bg-[#0F2318] border-gray-200 dark:border-[#1F3D28]'}`}>
                        {isCompleted ?
                        <CheckCircleIcon className="w-5 h-5 text-white" /> :
                        <step.icon
                          className={`w-4 h-4 ${isActive ? 'text-forest dark:text-gold' : 'text-gray-400 dark:text-gray-600'}`} />
                        }
                      </div>
                      <span
                        className={`text-xs font-medium hidden sm:block ${isCompleted ? 'text-forest dark:text-gold' : isActive ? 'text-gray-900 dark:text-white' : 'text-gray-400 dark:text-gray-600'}`}>
                        {step.title}
                      </span>
                    </div>
                    {index < 2 &&
                    <div
                      className={`flex-1 h-0.5 mx-3 transition-colors ${completedSteps.includes(index) ? 'bg-gold' : 'bg-gray-200 dark:bg-[#1F3D28]'}`} />
                    }
                  </Fragment>);
              })}
            </div>

            {/* Step Content */}
            <AnimatePresence mode="wait">
              {currentStep < 3 ?
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}>

                  <div className="mb-6">
                    <h3 className="font-heading text-xl font-bold text-gray-900 dark:text-white mb-1">
                      {STEPS[currentStep].title}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 font-body">
                      {STEPS[currentStep].description}
                    </p>
                  </div>

                  {/* Step 0: ID Upload */}
                  {currentStep === 0 &&
                <div
                  className={`border-2 border-dashed rounded-2xl p-10 text-center transition-colors cursor-pointer ${isDragOver ? 'border-forest bg-forest/5 dark:bg-forest/10' : uploadedFile ? 'border-gold bg-gold/5 dark:bg-gold/10' : 'border-gray-200 dark:border-[#1F3D28] hover:border-forest dark:hover:border-gold'}`}
                  onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                  onDragLeave={() => setIsDragOver(false)}
                  onDrop={(e) => { e.preventDefault(); setIsDragOver(false); setUploadedFile('national_id.jpg'); }}
                  onClick={() => setUploadedFile('national_id.jpg')}>
                      {uploadedFile ?
                  <div className="flex flex-col items-center gap-3">
                          <CheckCircleIcon className="w-12 h-12 text-gold" />
                          <p className="font-semibold text-gray-900 dark:text-white font-body">{uploadedFile}</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 font-body">Click to replace</p>
                        </div> :
                  <div className="flex flex-col items-center gap-3">
                          <UploadIcon className="w-10 h-10 text-gray-300 dark:text-gray-600" />
                          <p className="font-semibold text-gray-700 dark:text-gray-300 font-body">Drag & drop your National ID</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 font-body">JPG, PNG or PDF · Max 5MB · Both sides required</p>
                          <button className="mt-2 px-5 py-2 bg-forest text-white text-sm font-semibold rounded-lg hover:bg-forest-light transition-colors">Browse Files</button>
                        </div>
                  }
                    </div>
                }

                  {/* Step 1: KRA PIN */}
                  {currentStep === 1 &&
                <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 font-body mb-2">KRA PIN Number</label>
                        <div className="relative">
                          <KeyIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-forest dark:text-gold" />
                          <input
                        type="text"
                        placeholder="e.g. A001234567X"
                        value={kraPin}
                        onChange={(e) => setKraPin(e.target.value.toUpperCase())}
                        maxLength={11}
                        className="w-full pl-10 pr-4 py-3 text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-[#0F2318] rounded-xl border border-gray-200 dark:border-[#1F3D28] focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-all font-mono" />
                        </div>
                        <p className="text-xs text-gray-400 dark:text-gray-500 font-body mt-1.5">Your KRA PIN is used only for identity verification and is never stored</p>
                      </div>
                      <div className="flex items-start gap-3 p-4 bg-gold/5 dark:bg-gold/10 rounded-xl border border-gold/20">
                        <FileTextIcon className="w-4 h-4 text-gold flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-gray-600 dark:text-gray-400 font-body">Required by the Kenya Revenue Authority for all property transactions. Your data is encrypted and protected under Kenya's Data Protection Act 2019.</p>
                      </div>
                    </div>
                }

                  {/* Step 2: LR Number */}
                  {currentStep === 2 &&
                <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 font-body mb-2">Land Reference (LR) Number</label>
                        <div className="relative">
                          <MapIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-forest dark:text-gold" />
                          <input
                        type="text"
                        placeholder="e.g. LR/209/12345 or Nairobi/Block 123/456"
                        value={lrNumber}
                        onChange={(e) => setLrNumber(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-[#0F2318] rounded-xl border border-gray-200 dark:border-[#1F3D28] focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-all" />
                        </div>
                        <p className="text-xs text-gray-400 dark:text-gray-500 font-body mt-1.5">Found on your title deed. We'll verify this against the Ardhisasa database.</p>
                      </div>
                      <div className="flex items-center gap-3 p-4 bg-forest/5 dark:bg-forest/10 rounded-xl border border-forest/10 dark:border-forest/20">
                        <ShieldCheckIcon className="w-4 h-4 text-forest dark:text-gold flex-shrink-0" />
                        <p className="text-xs text-gray-600 dark:text-gray-400 font-body">Ardhisasa check confirms: ownership, encumbrances, caveats, and rates clearance. Takes ~30 seconds.</p>
                      </div>
                    </div>
                }

                  {/* Next Button */}
                  <button
                  onClick={handleNext}
                  disabled={isChecking}
                  className="mt-8 w-full flex items-center justify-center gap-2 py-4 bg-forest text-white font-semibold rounded-xl hover:bg-forest-light transition-colors disabled:opacity-70 text-sm">
                    {isChecking ?
                  <>
                        <motion.div
                      className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }} />
                        {currentStep === 2 ? 'Running Ardhisasa Check...' : 'Verifying...'}
                      </> :
                  <>
                        {currentStep === 2 ? 'Submit for Review' : 'Next Step'}
                        <ArrowRightIcon className="w-4 h-4" />
                      </>
                  }
                  </button>
                </motion.div> :

              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="text-center py-8">

                  <motion.div
                  className="flex items-center justify-center w-20 h-20 rounded-full bg-forest/10 dark:bg-forest/20 mx-auto mb-6"
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 0.5, delay: 0.2 }}>
                    <CheckCircleIcon className="w-10 h-10 text-forest dark:text-gold" />
                  </motion.div>
                  <h3 className="font-heading text-2xl font-bold text-gray-900 dark:text-white mb-3">KYC Submitted Successfully!</h3>
                  <p className="text-gray-500 dark:text-gray-400 font-body text-sm max-w-sm mx-auto mb-6">Your verification is under review. We'll notify you within 24 hours once your listing is approved and goes live.</p>
                  <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-gold/10 dark:bg-gold/20 rounded-full border border-gold/30">
                    <ShieldCheckIcon className="w-4 h-4 text-gold" />
                    <span className="text-sm font-semibold text-gold-dark dark:text-gold">Verification Pending</span>
                  </div>
                </motion.div>
              }
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>);
}