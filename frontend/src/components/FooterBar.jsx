import { motion } from 'framer-motion';
import { orderData, emiOptions as defaultEmiOptions } from '../data/mockData';

const FooterBar = ({ selectedEMI, ctaText, canProceed, isGrabCreditSelected, emiOptions, isLoading = false }) => {
  // Use persona-specific EMI options or default
  const activeEmiOptions = emiOptions || defaultEmiOptions;

  // Handle both camelCase and snake_case property names from API
  const selectedOption = activeEmiOptions.find(opt => opt.id === selectedEMI);
  const displayAmount = selectedEMI && isGrabCreditSelected
    ? (selectedOption?.monthlyPayment || selectedOption?.monthly_payment || 0)
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
          whileHover={canProceed && !isLoading ? { scale: 1.02 } : {}}
          whileTap={canProceed && !isLoading ? { scale: 0.98 } : {}}
          disabled={!canProceed || isLoading}
          className={`
            px-8 py-3 md:py-4 rounded-lg font-semibold text-base md:text-lg transition-all duration-200 flex items-center justify-center gap-2
            ${canProceed && !isLoading
              ? 'bg-grabcredit-600 hover:bg-grabcredit-700 text-white shadow-lg hover:shadow-xl shadow-grabcredit-200 cursor-pointer'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-60'
            }
          `}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing...
            </>
          ) : (
            ctaText
          )}
        </motion.button>
      </div>

      {/* EMI Info */}
      {selectedEMI && isGrabCreditSelected && activeEmiOptions && selectedOption && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-3 pt-3 border-t border-gray-100"
        >
          <p className="text-xs text-gray-500 text-center">
            {selectedOption.duration} month EMI •
            Total: ₹{(selectedOption.totalAmount || selectedOption.total_amount || 0).toLocaleString('en-IN')}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default FooterBar;
