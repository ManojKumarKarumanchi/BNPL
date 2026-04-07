import { motion } from 'framer-motion';
import { orderData, emiOptions as defaultEmiOptions } from '../data/mockData';

const FooterBar = ({ selectedEMI, ctaText, canProceed, isGrabCreditSelected, emiOptions }) => {
  // Use persona-specific EMI options or default
  const activeEmiOptions = emiOptions || defaultEmiOptions;

  const displayAmount = selectedEMI && isGrabCreditSelected
    ? activeEmiOptions.find(opt => opt.id === selectedEMI)?.monthlyPayment
    : orderData.pricing.total;

  const displayLabel = selectedEMI && isGrabCreditSelected
    ? 'per month'
    : 'Total';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="sticky bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 md:p-6 shadow-soft-lg md:relative md:shadow-none md:border-t-0 mt-6"
    >
      <div className="flex items-center justify-between gap-4">
        {/* Amount Display */}
        <div>
          <p className="text-xs text-gray-500 mb-0.5">{displayLabel}</p>
          <p className="text-2xl md:text-3xl font-bold text-gray-900">
            ₹{displayAmount?.toLocaleString('en-IN')}
          </p>
        </div>

        {/* CTA Button */}
        <motion.button
          whileHover={canProceed ? { scale: 1.02 } : {}}
          whileTap={canProceed ? { scale: 0.98 } : {}}
          disabled={!canProceed}
          className={`
            px-8 py-3 md:py-4 rounded-lg font-semibold text-base md:text-lg transition-all duration-200
            ${canProceed
              ? 'bg-grabcredit-600 hover:bg-grabcredit-700 text-white shadow-lg hover:shadow-xl shadow-grabcredit-200'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {ctaText}
        </motion.button>
      </div>

      {/* EMI Info */}
      {selectedEMI && isGrabCreditSelected && activeEmiOptions && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-3 pt-3 border-t border-gray-100"
        >
          <p className="text-xs text-gray-500 text-center">
            {activeEmiOptions.find(opt => opt.id === selectedEMI)?.duration} month EMI •
            Total: ₹{activeEmiOptions.find(opt => opt.id === selectedEMI)?.totalAmount.toLocaleString('en-IN')}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default FooterBar;
